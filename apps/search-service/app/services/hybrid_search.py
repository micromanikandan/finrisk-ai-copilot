"""Hybrid search service combining BM25 and vector similarity."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import structlog

from app.core.opensearch import get_opensearch_client
from app.services.embedding_service import EmbeddingService

logger = structlog.get_logger(__name__)


class HybridSearchService:
    """Hybrid search combining traditional keyword search (BM25) with vector similarity."""
    
    def __init__(self):
        self.opensearch_client = get_opensearch_client()
        self.embedding_service = EmbeddingService()
    
    async def search(
        self,
        query: str,
        indices: List[str],
        tenant_id: str,
        cell_id: str,
        size: int = 10,
        from_: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        boost_params: Optional[Dict[str, float]] = None,
        search_type: str = "hybrid"  # "hybrid", "keyword", "semantic"
    ) -> Dict[str, Any]:
        """
        Execute hybrid search combining keyword and semantic search.
        
        Args:
            query: Search query string
            indices: List of indices to search
            tenant_id: Tenant identifier
            cell_id: Cell identifier
            size: Number of results to return
            from_: Offset for pagination
            filters: Additional filters to apply
            boost_params: Boost parameters for different search components
            search_type: Type of search ("hybrid", "keyword", "semantic")
        """
        logger.info("Executing hybrid search", 
                   query=query, 
                   indices=indices, 
                   search_type=search_type)
        
        try:
            if search_type == "keyword":
                return await self._keyword_search(query, indices, tenant_id, cell_id, size, from_, filters)
            elif search_type == "semantic":
                return await self._semantic_search(query, indices, tenant_id, cell_id, size, from_, filters)
            else:
                return await self._hybrid_search(query, indices, tenant_id, cell_id, size, from_, filters, boost_params)
        except Exception as e:
            logger.error("Hybrid search failed", error=str(e), query=query)
            return self._empty_result()
    
    async def _hybrid_search(
        self,
        query: str,
        indices: List[str],
        tenant_id: str,
        cell_id: str,
        size: int,
        from_: int,
        filters: Optional[Dict[str, Any]],
        boost_params: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Execute hybrid search combining keyword and vector search."""
        
        # Default boost parameters
        default_boosts = {
            "keyword_boost": 1.0,
            "semantic_boost": 1.0,
            "title_boost": 2.0,
            "exact_match_boost": 3.0
        }
        boosts = {**default_boosts, **(boost_params or {})}
        
        # Generate embedding for the query
        query_embedding = await self.embedding_service.encode_text(query)
        
        # Build the hybrid query
        hybrid_query = {
            "query": {
                "bool": {
                    "should": [
                        # Traditional keyword search with boosting
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    f"title^{boosts['title_boost']}",
                                    "content",
                                    "description"
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                                "boost": boosts["keyword_boost"]
                            }
                        },
                        # Exact title match with high boost
                        {
                            "match_phrase": {
                                "title": {
                                    "query": query,
                                    "boost": boosts["exact_match_boost"]
                                }
                            }
                        },
                        # Vector similarity search
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": query_embedding.tolist(),
                                    "k": size * 2,  # Get more candidates for better ranking
                                    "boost": boosts["semantic_boost"]
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1,
                    "filter": self._build_filters(tenant_id, cell_id, filters)
                }
            },
            "highlight": {
                "fields": {
                    "title": {"number_of_fragments": 1},
                    "content": {"number_of_fragments": 3, "fragment_size": 150},
                    "description": {"number_of_fragments": 2}
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            },
            "sort": [
                "_score",
                {"created_at": {"order": "desc"}}
            ]
        }
        
        # Execute search across all indices
        search_results = []
        for index in indices:
            try:
                result = await self.opensearch_client.search(
                    index_name=index,
                    query=hybrid_query,
                    size=size,
                    from_=from_
                )
                
                # Add index information to results
                for hit in result["hits"]["hits"]:
                    hit["_index_name"] = index
                    hit["_search_type"] = "hybrid"
                
                search_results.append(result)
            except Exception as e:
                logger.error("Search failed for index", index=index, error=str(e))
        
        # Merge and rank results from all indices
        return self._merge_search_results(search_results, size, from_)
    
    async def _keyword_search(
        self,
        query: str,
        indices: List[str],
        tenant_id: str,
        cell_id: str,
        size: int,
        from_: int,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute pure keyword search using BM25."""
        
        keyword_query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content", "description"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        },
                        {
                            "match_phrase": {
                                "title": {
                                    "query": query,
                                    "boost": 5.0
                                }
                            }
                        }
                    ],
                    "filter": self._build_filters(tenant_id, cell_id, filters)
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {"fragment_size": 150},
                    "description": {}
                }
            }
        }
        
        search_results = []
        for index in indices:
            try:
                result = await self.opensearch_client.search(
                    index_name=index,
                    query=keyword_query,
                    size=size,
                    from_=from_
                )
                
                for hit in result["hits"]["hits"]:
                    hit["_index_name"] = index
                    hit["_search_type"] = "keyword"
                
                search_results.append(result)
            except Exception as e:
                logger.error("Keyword search failed for index", index=index, error=str(e))
        
        return self._merge_search_results(search_results, size, from_)
    
    async def _semantic_search(
        self,
        query: str,
        indices: List[str],
        tenant_id: str,
        cell_id: str,
        size: int,
        from_: int,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute pure semantic search using vector similarity."""
        
        # Generate embedding for the query
        query_embedding = await self.embedding_service.encode_text(query)
        
        semantic_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": query_embedding.tolist(),
                                    "k": size * 3  # Get more candidates
                                }
                            }
                        }
                    ],
                    "filter": self._build_filters(tenant_id, cell_id, filters)
                }
            }
        }
        
        search_results = []
        for index in indices:
            try:
                result = await self.opensearch_client.search(
                    index_name=index,
                    query=semantic_query,
                    size=size,
                    from_=from_
                )
                
                for hit in result["hits"]["hits"]:
                    hit["_index_name"] = index
                    hit["_search_type"] = "semantic"
                
                search_results.append(result)
            except Exception as e:
                logger.error("Semantic search failed for index", index=index, error=str(e))
        
        return self._merge_search_results(search_results, size, from_)
    
    def _build_filters(
        self,
        tenant_id: str,
        cell_id: str,
        additional_filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build filter conditions for the search query."""
        filters = [
            {"term": {"tenant_id": tenant_id}},
            {"term": {"cell_id": cell_id}}
        ]
        
        if additional_filters:
            for field, value in additional_filters.items():
                if isinstance(value, list):
                    filters.append({"terms": {field: value}})
                elif isinstance(value, dict):
                    # Handle range queries
                    if "gte" in value or "lte" in value or "gt" in value or "lt" in value:
                        filters.append({"range": {field: value}})
                    else:
                        filters.append({"term": {field: value}})
                else:
                    filters.append({"term": {field: value}})
        
        return filters
    
    def _merge_search_results(
        self,
        search_results: List[Dict[str, Any]],
        size: int,
        from_: int
    ) -> Dict[str, Any]:
        """Merge and rank results from multiple indices."""
        all_hits = []
        total_hits = 0
        
        for result in search_results:
            hits = result.get("hits", {})
            total_hits += hits.get("total", {}).get("value", 0)
            all_hits.extend(hits.get("hits", []))
        
        # Sort by score (descending)
        all_hits.sort(key=lambda x: x.get("_score", 0), reverse=True)
        
        # Apply pagination
        paginated_hits = all_hits[from_:from_ + size]
        
        return {
            "hits": {
                "total": {"value": total_hits, "relation": "eq"},
                "max_score": max((hit.get("_score", 0) for hit in all_hits), default=0),
                "hits": paginated_hits
            },
            "took": sum(result.get("took", 0) for result in search_results),
            "_shards": {
                "total": len(search_results),
                "successful": len(search_results),
                "skipped": 0,
                "failed": 0
            }
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty search result."""
        return {
            "hits": {
                "total": {"value": 0, "relation": "eq"},
                "max_score": 0,
                "hits": []
            },
            "took": 0,
            "_shards": {
                "total": 0,
                "successful": 0,
                "skipped": 0,
                "failed": 0
            }
        }
    
    async def search_suggestions(
        self,
        query: str,
        index_name: str,
        tenant_id: str,
        cell_id: str,
        field: str = "title.suggest",
        size: int = 5
    ) -> List[str]:
        """Get search suggestions using completion suggester."""
        
        suggestion_query = {
            "suggest": {
                "suggestions": {
                    "prefix": query,
                    "completion": {
                        "field": field,
                        "size": size,
                        "contexts": {
                            "tenant_id": [tenant_id],
                            "cell_id": [cell_id]
                        }
                    }
                }
            }
        }
        
        try:
            result = await self.opensearch_client.suggest(index_name, suggestion_query)
            suggestions = []
            
            for suggestion in result.get("suggestions", []):
                for option in suggestion.get("options", []):
                    suggestions.append(option.get("text", ""))
            
            return suggestions[:size]
        except Exception as e:
            logger.error("Suggestion query failed", error=str(e))
            return []
    
    async def get_facets(
        self,
        query: str,
        indices: List[str],
        tenant_id: str,
        cell_id: str,
        facet_fields: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get faceted search results for filtering."""
        
        facet_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title", "content", "description"]
                            }
                        }
                    ],
                    "filter": self._build_filters(tenant_id, cell_id, None)
                }
            },
            "size": 0,  # We only want aggregations
            "aggs": {}
        }
        
        # Add aggregations for each facet field
        for field in facet_fields:
            facet_query["aggs"][f"{field}_facet"] = {
                "terms": {
                    "field": field,
                    "size": 10
                }
            }
        
        facets = {}
        for index in indices:
            try:
                result = await self.opensearch_client.search(
                    index_name=index,
                    query=facet_query,
                    size=0
                )
                
                # Process aggregation results
                aggs = result.get("aggregations", {})
                for field in facet_fields:
                    facet_key = f"{field}_facet"
                    if facet_key in aggs:
                        if field not in facets:
                            facets[field] = []
                        
                        for bucket in aggs[facet_key].get("buckets", []):
                            facets[field].append({
                                "value": bucket["key"],
                                "count": bucket["doc_count"]
                            })
            except Exception as e:
                logger.error("Facet query failed for index", index=index, error=str(e))
        
        return facets
