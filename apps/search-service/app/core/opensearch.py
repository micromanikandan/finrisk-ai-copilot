"""OpenSearch client configuration and utilities."""

import json
from functools import lru_cache
from typing import Dict, Any, List, Optional, Union

from opensearchpy import AsyncOpenSearch, OpenSearch
from opensearchpy.exceptions import NotFoundError, RequestError
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class OpenSearchClient:
    """OpenSearch client wrapper with utilities."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenSearch(
            hosts=[{
                'host': self.settings.OPENSEARCH_HOST,
                'port': self.settings.OPENSEARCH_PORT,
                'use_ssl': self.settings.OPENSEARCH_USE_SSL,
            }],
            http_auth=(
                self.settings.OPENSEARCH_USERNAME,
                self.settings.OPENSEARCH_PASSWORD
            ) if self.settings.OPENSEARCH_USERNAME else None,
            verify_certs=self.settings.OPENSEARCH_VERIFY_CERTS,
            ssl_show_warn=False,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )
    
    async def ping(self) -> bool:
        """Test connection to OpenSearch."""
        try:
            response = await self.client.ping()
            logger.info("OpenSearch ping successful", response=response)
            return True
        except Exception as e:
            logger.error("OpenSearch ping failed", error=str(e))
            return False
    
    async def close(self) -> None:
        """Close the client connection."""
        await self.client.close()
    
    async def create_index(self, index_name: str, mapping: Dict[str, Any], settings: Optional[Dict[str, Any]] = None) -> bool:
        """Create an index with mapping and settings."""
        try:
            body = {"mappings": mapping}
            if settings:
                body["settings"] = settings
            
            await self.client.indices.create(index=index_name, body=body)
            logger.info("Index created successfully", index=index_name)
            return True
        except RequestError as e:
            if 'resource_already_exists_exception' in str(e):
                logger.info("Index already exists", index=index_name)
                return True
            logger.error("Failed to create index", index=index_name, error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error creating index", index=index_name, error=str(e))
            return False
    
    async def delete_index(self, index_name: str) -> bool:
        """Delete an index."""
        try:
            await self.client.indices.delete(index=index_name)
            logger.info("Index deleted successfully", index=index_name)
            return True
        except NotFoundError:
            logger.info("Index not found for deletion", index=index_name)
            return True
        except Exception as e:
            logger.error("Failed to delete index", index=index_name, error=str(e))
            return False
    
    async def index_exists(self, index_name: str) -> bool:
        """Check if an index exists."""
        try:
            return await self.client.indices.exists(index=index_name)
        except Exception as e:
            logger.error("Error checking index existence", index=index_name, error=str(e))
            return False
    
    async def index_document(self, index_name: str, document: Dict[str, Any], doc_id: Optional[str] = None) -> Optional[str]:
        """Index a single document."""
        try:
            response = await self.client.index(
                index=index_name,
                body=document,
                id=doc_id,
                refresh='wait_for'
            )
            return response['_id']
        except Exception as e:
            logger.error("Failed to index document", index=index_name, error=str(e))
            return None
    
    async def bulk_index(self, index_name: str, documents: List[Dict[str, Any]], doc_ids: Optional[List[str]] = None) -> Dict[str, int]:
        """Bulk index multiple documents."""
        try:
            body = []
            for i, doc in enumerate(documents):
                action = {"index": {"_index": index_name}}
                if doc_ids and i < len(doc_ids):
                    action["index"]["_id"] = doc_ids[i]
                body.append(action)
                body.append(doc)
            
            response = await self.client.bulk(body=body, refresh='wait_for')
            
            # Count successful and failed operations
            successful = 0
            failed = 0
            for item in response['items']:
                if 'index' in item:
                    if item['index']['status'] in [200, 201]:
                        successful += 1
                    else:
                        failed += 1
            
            logger.info("Bulk indexing completed", 
                       index=index_name, 
                       successful=successful, 
                       failed=failed)
            
            return {"successful": successful, "failed": failed}
        except Exception as e:
            logger.error("Bulk indexing failed", index=index_name, error=str(e))
            return {"successful": 0, "failed": len(documents)}
    
    async def search(self, index_name: str, query: Dict[str, Any], size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """Execute a search query."""
        try:
            response = await self.client.search(
                index=index_name,
                body=query,
                size=size,
                from_=from_
            )
            return response
        except Exception as e:
            logger.error("Search query failed", index=index_name, error=str(e))
            return {"hits": {"total": {"value": 0}, "hits": []}}
    
    async def multi_search(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple search queries."""
        try:
            body = []
            for query in queries:
                body.append({"index": query.get("index", "_all")})
                body.append(query["query"])
            
            response = await self.client.msearch(body=body)
            return response["responses"]
        except Exception as e:
            logger.error("Multi-search failed", error=str(e))
            return [{"hits": {"total": {"value": 0}, "hits": []}} for _ in queries]
    
    async def get_document(self, index_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            response = await self.client.get(index=index_name, id=doc_id)
            return response["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            logger.error("Failed to get document", index=index_name, doc_id=doc_id, error=str(e))
            return None
    
    async def update_document(self, index_name: str, doc_id: str, update: Dict[str, Any]) -> bool:
        """Update a document."""
        try:
            await self.client.update(
                index=index_name,
                id=doc_id,
                body={"doc": update},
                refresh='wait_for'
            )
            return True
        except Exception as e:
            logger.error("Failed to update document", index=index_name, doc_id=doc_id, error=str(e))
            return False
    
    async def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document."""
        try:
            await self.client.delete(index=index_name, id=doc_id, refresh='wait_for')
            return True
        except NotFoundError:
            return True
        except Exception as e:
            logger.error("Failed to delete document", index=index_name, doc_id=doc_id, error=str(e))
            return False
    
    async def count_documents(self, index_name: str, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query."""
        try:
            body = {"query": query} if query else None
            response = await self.client.count(index=index_name, body=body)
            return response["count"]
        except Exception as e:
            logger.error("Failed to count documents", index=index_name, error=str(e))
            return 0
    
    async def suggest(self, index_name: str, suggestion_query: Dict[str, Any]) -> Dict[str, Any]:
        """Get search suggestions."""
        try:
            response = await self.client.search(
                index=index_name,
                body={"suggest": suggestion_query}
            )
            return response.get("suggest", {})
        except Exception as e:
            logger.error("Suggestion query failed", index=index_name, error=str(e))
            return {}
    
    async def analyze_text(self, index_name: str, text: str, analyzer: str = "standard") -> List[str]:
        """Analyze text using OpenSearch analyzers."""
        try:
            response = await self.client.indices.analyze(
                index=index_name,
                body={
                    "analyzer": analyzer,
                    "text": text
                }
            )
            return [token["token"] for token in response["tokens"]]
        except Exception as e:
            logger.error("Text analysis failed", index=index_name, error=str(e))
            return []


@lru_cache()
def get_opensearch_client() -> OpenSearchClient:
    """Get cached OpenSearch client."""
    return OpenSearchClient()


# Common index mappings and settings
DOCUMENT_INDEX_MAPPING = {
    "properties": {
        "title": {
            "type": "text",
            "analyzer": "standard",
            "fields": {
                "keyword": {"type": "keyword"},
                "suggest": {
                    "type": "completion",
                    "analyzer": "simple"
                }
            }
        },
        "content": {
            "type": "text",
            "analyzer": "standard"
        },
        "content_vector": {
            "type": "knn_vector",
            "dimension": 384,  # sentence-transformers dimension
            "method": {
                "name": "hnsw",
                "space_type": "cosinesimil",
                "engine": "nmslib"
            }
        },
        "document_type": {"type": "keyword"},
        "source": {"type": "keyword"},
        "case_id": {"type": "keyword"},
        "entity_ids": {"type": "keyword"},
        "tags": {"type": "keyword"},
        "classification": {"type": "keyword"},
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"},
        "tenant_id": {"type": "keyword"},
        "cell_id": {"type": "keyword"},
        "metadata": {"type": "object", "enabled": False}
    }
}

ENTITY_INDEX_MAPPING = {
    "properties": {
        "name": {
            "type": "text",
            "analyzer": "standard",
            "fields": {
                "keyword": {"type": "keyword"},
                "suggest": {
                    "type": "completion",
                    "analyzer": "simple"
                }
            }
        },
        "entity_type": {"type": "keyword"},
        "external_id": {"type": "keyword"},
        "attributes": {"type": "object"},
        "risk_score": {"type": "float"},
        "embedding": {
            "type": "knn_vector",
            "dimension": 384,
            "method": {
                "name": "hnsw",
                "space_type": "cosinesimil",
                "engine": "nmslib"
            }
        },
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"},
        "tenant_id": {"type": "keyword"},
        "cell_id": {"type": "keyword"}
    }
}

CASE_INDEX_MAPPING = {
    "properties": {
        "case_number": {"type": "keyword"},
        "title": {
            "type": "text",
            "analyzer": "standard",
            "fields": {"keyword": {"type": "keyword"}}
        },
        "description": {"type": "text"},
        "case_type": {"type": "keyword"},
        "priority": {"type": "keyword"},
        "status": {"type": "keyword"},
        "assigned_to": {"type": "keyword"},
        "created_by": {"type": "keyword"},
        "tags": {"type": "keyword"},
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"},
        "tenant_id": {"type": "keyword"},
        "cell_id": {"type": "keyword"},
        "metadata": {"type": "object", "enabled": False}
    }
}

INDEX_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "index.knn": True,
    "analysis": {
        "analyzer": {
            "custom_text_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "stop",
                    "snowball"
                ]
            }
        }
    }
}
