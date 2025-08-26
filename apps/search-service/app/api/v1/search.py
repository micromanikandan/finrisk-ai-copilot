"""Search API endpoints."""

from typing import Dict, Any, List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.services.hybrid_search import HybridSearchService
from app.services.search_analytics import SearchAnalyticsService

logger = structlog.get_logger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    indices: List[str] = Field(default=["documents", "cases", "entities"], description="Indices to search")
    search_type: str = Field(default="hybrid", pattern="^(hybrid|keyword|semantic)$", description="Type of search")
    size: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    from_: int = Field(default=0, ge=0, alias="from", description="Offset for pagination")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filters")
    boost_params: Optional[Dict[str, float]] = Field(default=None, description="Boost parameters")
    include_facets: bool = Field(default=False, description="Include faceted results")
    facet_fields: List[str] = Field(default=[], description="Fields for faceted search")


class SearchHit(BaseModel):
    """Search result hit model."""
    id: str
    score: float
    source: Dict[str, Any]
    index: str
    search_type: str
    highlights: Optional[Dict[str, List[str]]] = None


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    total_hits: int
    max_score: float
    took_ms: int
    hits: List[SearchHit]
    facets: Optional[Dict[str, List[Dict[str, Any]]]] = None
    suggestions: Optional[List[str]] = None


class SuggestionRequest(BaseModel):
    """Search suggestion request model."""
    query: str = Field(..., min_length=1, max_length=100)
    indices: List[str] = Field(default=["documents", "cases", "entities"])
    size: int = Field(default=5, ge=1, le=20)


@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SearchResponse:
    """
    Execute a search query across specified indices.
    
    Supports multiple search types:
    - hybrid: Combines keyword and semantic search
    - keyword: Traditional BM25 keyword search
    - semantic: Vector similarity search
    """
    logger.info("Executing search", 
               query=request.query, 
               search_type=request.search_type,
               user=current_user["sub"])
    
    try:
        hybrid_search = HybridSearchService()
        analytics = SearchAnalyticsService()
        
        # Execute the search
        search_result = await hybrid_search.search(
            query=request.query,
            indices=request.indices,
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"],
            size=request.size,
            from_=request.from_,
            filters=request.filters,
            boost_params=request.boost_params,
            search_type=request.search_type
        )
        
        # Get facets if requested
        facets = None
        if request.include_facets and request.facet_fields:
            facets = await hybrid_search.get_facets(
                query=request.query,
                indices=request.indices,
                tenant_id=current_user["tenant_id"],
                cell_id=current_user["cell_id"],
                facet_fields=request.facet_fields
            )
        
        # Process hits
        hits = []
        for hit in search_result["hits"]["hits"]:
            hits.append(SearchHit(
                id=hit["_id"],
                score=hit["_score"],
                source=hit["_source"],
                index=hit.get("_index_name", hit["_index"]),
                search_type=hit.get("_search_type", request.search_type),
                highlights=hit.get("highlight")
            ))
        
        # Log search analytics
        await analytics.log_search(
            query=request.query,
            search_type=request.search_type,
            indices=request.indices,
            total_hits=search_result["hits"]["total"]["value"],
            user_id=current_user["sub"],
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        return SearchResponse(
            query=request.query,
            total_hits=search_result["hits"]["total"]["value"],
            max_score=search_result["hits"]["max_score"],
            took_ms=search_result["took"],
            hits=hits,
            facets=facets
        )
        
    except Exception as e:
        logger.error("Search failed", error=str(e), query=request.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/suggestions")
async def get_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Query for suggestions"),
    indices: List[str] = Query(default=["documents"], description="Indices to search for suggestions"),
    size: int = Query(default=5, ge=1, le=20, description="Number of suggestions"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[str]:
    """Get search suggestions for autocomplete."""
    
    logger.info("Getting search suggestions", query=q, user=current_user["sub"])
    
    try:
        hybrid_search = HybridSearchService()
        suggestions = []
        
        # Get suggestions from each index
        for index in indices:
            index_suggestions = await hybrid_search.search_suggestions(
                query=q,
                index_name=index,
                tenant_id=current_user["tenant_id"],
                cell_id=current_user["cell_id"],
                size=size
            )
            suggestions.extend(index_suggestions)
        
        # Remove duplicates and limit results
        unique_suggestions = list(dict.fromkeys(suggestions))[:size]
        
        return unique_suggestions
        
    except Exception as e:
        logger.error("Suggestions failed", error=str(e), query=q)
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")


@router.post("/similar")
async def find_similar_documents(
    document_id: str,
    index_name: str,
    size: int = Query(default=10, ge=1, le=50),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SearchResponse:
    """Find documents similar to a given document using vector similarity."""
    
    logger.info("Finding similar documents", 
               document_id=document_id, 
               index=index_name,
               user=current_user["sub"])
    
    try:
        hybrid_search = HybridSearchService()
        opensearch_client = hybrid_search.opensearch_client
        
        # Get the source document
        source_doc = await opensearch_client.get_document(index_name, document_id)
        if not source_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if document has embeddings
        if "content_vector" not in source_doc:
            raise HTTPException(status_code=400, detail="Document does not have vector embeddings")
        
        # Build similarity query
        similarity_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": source_doc["content_vector"],
                                    "k": size + 1  # +1 to exclude the source document
                                }
                            }
                        }
                    ],
                    "must_not": [
                        {"term": {"_id": document_id}}  # Exclude the source document
                    ],
                    "filter": [
                        {"term": {"tenant_id": current_user["tenant_id"]}},
                        {"term": {"cell_id": current_user["cell_id"]}}
                    ]
                }
            }
        }
        
        # Execute similarity search
        result = await opensearch_client.search(index_name, similarity_query, size=size)
        
        # Process hits
        hits = []
        for hit in result["hits"]["hits"]:
            hits.append(SearchHit(
                id=hit["_id"],
                score=hit["_score"],
                source=hit["_source"],
                index=index_name,
                search_type="similarity"
            ))
        
        return SearchResponse(
            query=f"Similar to document {document_id}",
            total_hits=result["hits"]["total"]["value"],
            max_score=result["hits"]["max_score"],
            took_ms=result["took"],
            hits=hits
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Similar documents search failed", error=str(e), document_id=document_id)
        raise HTTPException(status_code=500, detail=f"Similar documents search failed: {str(e)}")


@router.get("/popular-queries")
async def get_popular_queries(
    limit: int = Query(default=10, ge=1, le=50),
    days: int = Query(default=7, ge=1, le=30),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get popular search queries for the tenant."""
    
    try:
        analytics = SearchAnalyticsService()
        
        popular_queries = await analytics.get_popular_queries(
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"],
            days=days,
            limit=limit
        )
        
        return popular_queries
        
    except Exception as e:
        logger.error("Failed to get popular queries", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get popular queries: {str(e)}")


@router.get("/trending-terms")
async def get_trending_terms(
    limit: int = Query(default=20, ge=1, le=100),
    hours: int = Query(default=24, ge=1, le=168),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get trending search terms."""
    
    try:
        analytics = SearchAnalyticsService()
        
        trending_terms = await analytics.get_trending_terms(
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"],
            hours=hours,
            limit=limit
        )
        
        return trending_terms
        
    except Exception as e:
        logger.error("Failed to get trending terms", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get trending terms: {str(e)}")


@router.post("/feedback")
async def submit_search_feedback(
    query: str,
    document_id: str,
    relevant: bool,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Submit relevance feedback for search results."""
    
    try:
        analytics = SearchAnalyticsService()
        
        await analytics.log_feedback(
            query=query,
            document_id=document_id,
            relevant=relevant,
            user_id=current_user["sub"],
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        return {"message": "Feedback submitted successfully"}
        
    except Exception as e:
        logger.error("Failed to submit feedback", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")
