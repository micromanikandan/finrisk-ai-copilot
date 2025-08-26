"""Entity resolution service for deduplication and matching."""

import asyncio
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import structlog

from app.core.neo4j_client import get_neo4j_client
from app.core.redis_client import get_redis_client
from app.models.entity import Entity, EntityType, EntityMatch, MatchConfidence

logger = structlog.get_logger(__name__)


class MatchMethod(str, Enum):
    """Entity matching methods."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    ML_CLUSTERING = "ml_clustering"


@dataclass
class EntityCandidate:
    """Entity candidate for matching."""
    entity_id: str
    name: str
    entity_type: EntityType
    attributes: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    source_confidence: float = 1.0


class EntityResolutionService:
    """Service for entity resolution, deduplication, and matching."""
    
    def __init__(self):
        self.neo4j_client = None
        self.redis_client = None
        self.embedding_model = None
        self.clustering_model = None
        self.similarity_threshold = 0.85
        self.fuzzy_threshold = 80  # Fuzzy matching threshold (0-100)
    
    async def initialize(self) -> None:
        """Initialize the entity resolution service."""
        logger.info("Initializing entity resolution service")
        
        self.neo4j_client = get_neo4j_client()
        self.redis_client = get_redis_client()
        
        # Initialize embedding model for semantic matching
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize clustering model
        self.clustering_model = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
        
        logger.info("Entity resolution service initialized successfully")
    
    async def resolve_entity(
        self,
        entity_data: Dict[str, Any],
        tenant_id: str,
        cell_id: str,
        match_method: MatchMethod = MatchMethod.HYBRID,
        create_if_not_found: bool = True
    ) -> Dict[str, Any]:
        """
        Resolve an entity by finding matches or creating a new one.
        
        Args:
            entity_data: Entity information to resolve
            tenant_id: Tenant identifier
            cell_id: Cell identifier
            match_method: Method to use for matching
            create_if_not_found: Whether to create entity if no match found
        """
        logger.info("Resolving entity", 
                   name=entity_data.get("name"),
                   entity_type=entity_data.get("entity_type"),
                   method=match_method.value)
        
        try:
            # Create entity candidate
            candidate = EntityCandidate(
                entity_id=str(uuid.uuid4()),
                name=entity_data["name"],
                entity_type=EntityType(entity_data["entity_type"]),
                attributes=entity_data.get("attributes", {}),
                source_confidence=entity_data.get("confidence", 1.0)
            )
            
            # Generate embedding for semantic matching
            if match_method in [MatchMethod.SEMANTIC, MatchMethod.HYBRID]:
                candidate.embedding = await self._generate_embedding(candidate)
            
            # Find potential matches
            matches = await self._find_matches(candidate, tenant_id, cell_id, match_method)
            
            if matches:
                # Return best match
                best_match = max(matches, key=lambda m: m.confidence_score)
                
                if best_match.confidence_score >= self.similarity_threshold:
                    # Update existing entity with new information
                    updated_entity = await self._merge_entity_data(
                        best_match.matched_entity_id,
                        entity_data,
                        tenant_id,
                        cell_id
                    )
                    
                    return {
                        "success": True,
                        "action": "matched",
                        "entity": updated_entity,
                        "match_confidence": best_match.confidence_score,
                        "match_method": best_match.match_method,
                        "alternatives": [m.to_dict() for m in matches[1:5]]  # Top 5 alternatives
                    }
            
            # No good match found - create new entity if requested
            if create_if_not_found:
                new_entity = await self._create_entity(candidate, tenant_id, cell_id)
                
                return {
                    "success": True,
                    "action": "created",
                    "entity": new_entity,
                    "match_confidence": 1.0,
                    "alternatives": [m.to_dict() for m in matches[:5]] if matches else []
                }
            else:
                return {
                    "success": True,
                    "action": "no_match",
                    "entity": None,
                    "alternatives": [m.to_dict() for m in matches[:5]] if matches else []
                }
        
        except Exception as e:
            logger.error("Entity resolution failed", error=str(e), entity=entity_data.get("name"))
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    async def _find_matches(
        self,
        candidate: EntityCandidate,
        tenant_id: str,
        cell_id: str,
        match_method: MatchMethod
    ) -> List[EntityMatch]:
        """Find potential entity matches using specified method."""
        
        matches = []
        
        if match_method == MatchMethod.EXACT:
            matches.extend(await self._exact_match(candidate, tenant_id, cell_id))
        
        elif match_method == MatchMethod.FUZZY:
            matches.extend(await self._fuzzy_match(candidate, tenant_id, cell_id))
        
        elif match_method == MatchMethod.SEMANTIC:
            matches.extend(await self._semantic_match(candidate, tenant_id, cell_id))
        
        elif match_method == MatchMethod.HYBRID:
            # Combine multiple methods
            exact_matches = await self._exact_match(candidate, tenant_id, cell_id)
            fuzzy_matches = await self._fuzzy_match(candidate, tenant_id, cell_id)
            semantic_matches = await self._semantic_match(candidate, tenant_id, cell_id)
            
            # Merge and deduplicate matches
            all_matches = exact_matches + fuzzy_matches + semantic_matches
            matches = self._deduplicate_matches(all_matches)
        
        elif match_method == MatchMethod.ML_CLUSTERING:
            matches.extend(await self._ml_clustering_match(candidate, tenant_id, cell_id))
        
        # Sort by confidence score
        matches.sort(key=lambda m: m.confidence_score, reverse=True)
        
        return matches
    
    async def _exact_match(
        self,
        candidate: EntityCandidate,
        tenant_id: str,
        cell_id: str
    ) -> List[EntityMatch]:
        """Find exact name matches."""
        
        query = """
        MATCH (e:Entity {name: $name, entity_type: $entity_type, tenant_id: $tenant_id, cell_id: $cell_id})
        RETURN e.id as entity_id, e.name as name, e.attributes as attributes
        LIMIT 10
        """
        
        result = await self.neo4j_client.run_query(
            query,
            name=candidate.name,
            entity_type=candidate.entity_type.value,
            tenant_id=tenant_id,
            cell_id=cell_id
        )
        
        matches = []
        for record in result:
            matches.append(EntityMatch(
                candidate_entity_id=candidate.entity_id,
                matched_entity_id=record["entity_id"],
                confidence_score=1.0,
                match_method=MatchMethod.EXACT,
                match_details={
                    "matched_name": record["name"],
                    "attributes": record["attributes"]
                }
            ))
        
        return matches
    
    async def _fuzzy_match(
        self,
        candidate: EntityCandidate,
        tenant_id: str,
        cell_id: str
    ) -> List[EntityMatch]:
        """Find fuzzy string matches."""
        
        # Get similar entities from Neo4j
        query = """
        MATCH (e:Entity {entity_type: $entity_type, tenant_id: $tenant_id, cell_id: $cell_id})
        RETURN e.id as entity_id, e.name as name, e.attributes as attributes
        LIMIT 100
        """
        
        result = await self.neo4j_client.run_query(
            query,
            entity_type=candidate.entity_type.value,
            tenant_id=tenant_id,
            cell_id=cell_id
        )
        
        matches = []
        for record in result:
            # Calculate fuzzy similarity
            similarity = fuzz.ratio(candidate.name.lower(), record["name"].lower())
            
            if similarity >= self.fuzzy_threshold:
                confidence = similarity / 100.0
                
                matches.append(EntityMatch(
                    candidate_entity_id=candidate.entity_id,
                    matched_entity_id=record["entity_id"],
                    confidence_score=confidence,
                    match_method=MatchMethod.FUZZY,
                    match_details={
                        "fuzzy_score": similarity,
                        "matched_name": record["name"],
                        "attributes": record["attributes"]
                    }
                ))
        
        return matches
    
    async def _semantic_match(
        self,
        candidate: EntityCandidate,
        tenant_id: str,
        cell_id: str
    ) -> List[EntityMatch]:
        """Find semantic similarity matches using embeddings."""
        
        if candidate.embedding is None:
            return []
        
        # Get entities with embeddings from Redis cache or Neo4j
        cached_embeddings = await self._get_cached_embeddings(
            candidate.entity_type, tenant_id, cell_id
        )
        
        if not cached_embeddings:
            return []
        
        # Calculate cosine similarities
        similarities = cosine_similarity([candidate.embedding], cached_embeddings["embeddings"])[0]
        
        matches = []
        for i, similarity in enumerate(similarities):
            if similarity >= self.similarity_threshold:
                entity_info = cached_embeddings["entities"][i]
                
                matches.append(EntityMatch(
                    candidate_entity_id=candidate.entity_id,
                    matched_entity_id=entity_info["id"],
                    confidence_score=float(similarity),
                    match_method=MatchMethod.SEMANTIC,
                    match_details={
                        "semantic_similarity": float(similarity),
                        "matched_name": entity_info["name"],
                        "attributes": entity_info.get("attributes", {})
                    }
                ))
        
        return matches
    
    async def _ml_clustering_match(
        self,
        candidate: EntityCandidate,
        tenant_id: str,
        cell_id: str
    ) -> List[EntityMatch]:
        """Find matches using ML clustering techniques."""
        
        # Get all entities of same type for clustering
        entities_data = await self._get_entities_for_clustering(
            candidate.entity_type, tenant_id, cell_id
        )
        
        if len(entities_data) < 3:  # Need minimum entities for clustering
            return []
        
        # Prepare features for clustering
        features = []
        entity_ids = []
        
        for entity in entities_data:
            feature_vector = await self._extract_features(entity)
            features.append(feature_vector)
            entity_ids.append(entity["id"])
        
        # Add candidate to features
        candidate_features = await self._extract_features({
            "name": candidate.name,
            "attributes": candidate.attributes
        })
        features.append(candidate_features)
        entity_ids.append(candidate.entity_id)
        
        # Perform clustering
        features_array = np.array(features)
        cluster_labels = self.clustering_model.fit_predict(features_array)
        
        # Find entities in same cluster as candidate
        candidate_cluster = cluster_labels[-1]
        matches = []
        
        if candidate_cluster != -1:  # Not noise
            cluster_indices = np.where(cluster_labels == candidate_cluster)[0]
            
            for idx in cluster_indices[:-1]:  # Exclude candidate itself
                entity_id = entity_ids[idx]
                entity_data = entities_data[idx]
                
                # Calculate confidence based on cluster density
                cluster_size = len(cluster_indices)
                confidence = min(0.9, 0.5 + (cluster_size - 2) * 0.1)
                
                matches.append(EntityMatch(
                    candidate_entity_id=candidate.entity_id,
                    matched_entity_id=entity_id,
                    confidence_score=confidence,
                    match_method=MatchMethod.ML_CLUSTERING,
                    match_details={
                        "cluster_id": int(candidate_cluster),
                        "cluster_size": cluster_size,
                        "matched_name": entity_data["name"],
                        "attributes": entity_data.get("attributes", {})
                    }
                ))
        
        return matches
    
    async def _generate_embedding(self, candidate: EntityCandidate) -> np.ndarray:
        """Generate embedding for entity."""
        
        # Combine name and key attributes for embedding
        text_for_embedding = candidate.name
        
        if candidate.attributes:
            # Add important attributes to the text
            important_attrs = ["address", "email", "phone", "business_name", "registration_number"]
            attr_texts = []
            
            for attr in important_attrs:
                if attr in candidate.attributes and candidate.attributes[attr]:
                    attr_texts.append(f"{attr}: {candidate.attributes[attr]}")
            
            if attr_texts:
                text_for_embedding += " " + " ".join(attr_texts)
        
        # Generate embedding
        embedding = self.embedding_model.encode([text_for_embedding])[0]
        return embedding
    
    async def _get_cached_embeddings(
        self,
        entity_type: EntityType,
        tenant_id: str,
        cell_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached embeddings for entities."""
        
        cache_key = f"embeddings:{entity_type.value}:{tenant_id}:{cell_id}"
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return eval(cached_data)  # Use orjson in production
        except Exception as e:
            logger.warning("Failed to get cached embeddings", error=str(e))
        
        # If not cached, generate and cache
        return await self._generate_and_cache_embeddings(entity_type, tenant_id, cell_id)
    
    async def _generate_and_cache_embeddings(
        self,
        entity_type: EntityType,
        tenant_id: str,
        cell_id: str
    ) -> Dict[str, Any]:
        """Generate and cache embeddings for entities."""
        
        # Get entities from Neo4j
        query = """
        MATCH (e:Entity {entity_type: $entity_type, tenant_id: $tenant_id, cell_id: $cell_id})
        RETURN e.id as id, e.name as name, e.attributes as attributes
        LIMIT 1000
        """
        
        result = await self.neo4j_client.run_query(
            query,
            entity_type=entity_type.value,
            tenant_id=tenant_id,
            cell_id=cell_id
        )
        
        if not result:
            return {"entities": [], "embeddings": []}
        
        # Generate embeddings
        texts = []
        entities = []
        
        for record in result:
            entity = {
                "id": record["id"],
                "name": record["name"],
                "attributes": record.get("attributes", {})
            }
            entities.append(entity)
            
            # Prepare text for embedding
            text = record["name"]
            if record.get("attributes"):
                important_attrs = ["address", "email", "phone", "business_name"]
                attr_texts = []
                
                for attr in important_attrs:
                    if attr in record["attributes"] and record["attributes"][attr]:
                        attr_texts.append(f"{attr}: {record['attributes'][attr]}")
                
                if attr_texts:
                    text += " " + " ".join(attr_texts)
            
            texts.append(text)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Cache the results
        cache_data = {
            "entities": entities,
            "embeddings": embeddings.tolist()
        }
        
        cache_key = f"embeddings:{entity_type.value}:{tenant_id}:{cell_id}"
        try:
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                str(cache_data)  # Use orjson in production
            )
        except Exception as e:
            logger.warning("Failed to cache embeddings", error=str(e))
        
        return {
            "entities": entities,
            "embeddings": embeddings
        }
    
    def _deduplicate_matches(self, matches: List[EntityMatch]) -> List[EntityMatch]:
        """Remove duplicate matches and keep highest confidence."""
        
        entity_matches = {}
        
        for match in matches:
            entity_id = match.matched_entity_id
            
            if entity_id not in entity_matches:
                entity_matches[entity_id] = match
            else:
                # Keep match with higher confidence
                if match.confidence_score > entity_matches[entity_id].confidence_score:
                    entity_matches[entity_id] = match
        
        return list(entity_matches.values())
    
    async def _extract_features(self, entity_data: Dict[str, Any]) -> np.ndarray:
        """Extract features for ML clustering."""
        
        features = []
        
        # Name length
        features.append(len(entity_data["name"]))
        
        # Number of words in name
        features.append(len(entity_data["name"].split()))
        
        # Has email
        features.append(1 if entity_data.get("attributes", {}).get("email") else 0)
        
        # Has phone
        features.append(1 if entity_data.get("attributes", {}).get("phone") else 0)
        
        # Has address
        features.append(1 if entity_data.get("attributes", {}).get("address") else 0)
        
        # Number of attributes
        features.append(len(entity_data.get("attributes", {})))
        
        return np.array(features)
    
    async def _get_entities_for_clustering(
        self,
        entity_type: EntityType,
        tenant_id: str,
        cell_id: str
    ) -> List[Dict[str, Any]]:
        """Get entities for clustering analysis."""
        
        query = """
        MATCH (e:Entity {entity_type: $entity_type, tenant_id: $tenant_id, cell_id: $cell_id})
        RETURN e.id as id, e.name as name, e.attributes as attributes
        LIMIT 500
        """
        
        result = await self.neo4j_client.run_query(
            query,
            entity_type=entity_type.value,
            tenant_id=tenant_id,
            cell_id=cell_id
        )
        
        return [dict(record) for record in result]
    
    async def _create_entity(
        self,
        candidate: EntityCandidate,
        tenant_id: str,
        cell_id: str
    ) -> Dict[str, Any]:
        """Create a new entity in Neo4j."""
        
        entity_id = str(uuid.uuid4())
        
        query = """
        CREATE (e:Entity {
            id: $entity_id,
            name: $name,
            entity_type: $entity_type,
            attributes: $attributes,
            created_at: datetime(),
            updated_at: datetime(),
            tenant_id: $tenant_id,
            cell_id: $cell_id
        })
        RETURN e
        """
        
        await self.neo4j_client.run_query(
            query,
            entity_id=entity_id,
            name=candidate.name,
            entity_type=candidate.entity_type.value,
            attributes=candidate.attributes,
            tenant_id=tenant_id,
            cell_id=cell_id
        )
        
        return {
            "id": entity_id,
            "name": candidate.name,
            "entity_type": candidate.entity_type.value,
            "attributes": candidate.attributes,
            "tenant_id": tenant_id,
            "cell_id": cell_id,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _merge_entity_data(
        self,
        entity_id: str,
        new_data: Dict[str, Any],
        tenant_id: str,
        cell_id: str
    ) -> Dict[str, Any]:
        """Merge new data into existing entity."""
        
        # Get existing entity
        query = """
        MATCH (e:Entity {id: $entity_id, tenant_id: $tenant_id, cell_id: $cell_id})
        RETURN e
        """
        
        result = await self.neo4j_client.run_query(
            query,
            entity_id=entity_id,
            tenant_id=tenant_id,
            cell_id=cell_id
        )
        
        if not result:
            raise ValueError(f"Entity {entity_id} not found")
        
        existing_entity = dict(result[0]["e"])
        
        # Merge attributes
        merged_attributes = existing_entity.get("attributes", {})
        new_attributes = new_data.get("attributes", {})
        
        for key, value in new_attributes.items():
            if key not in merged_attributes or not merged_attributes[key]:
                merged_attributes[key] = value
            elif isinstance(value, list):
                # Merge lists
                existing_list = merged_attributes.get(key, [])
                if isinstance(existing_list, list):
                    merged_attributes[key] = list(set(existing_list + value))
        
        # Update entity
        update_query = """
        MATCH (e:Entity {id: $entity_id, tenant_id: $tenant_id, cell_id: $cell_id})
        SET e.attributes = $attributes,
            e.updated_at = datetime()
        RETURN e
        """
        
        await self.neo4j_client.run_query(
            update_query,
            entity_id=entity_id,
            attributes=merged_attributes,
            tenant_id=tenant_id,
            cell_id=cell_id
        )
        
        return {
            "id": entity_id,
            "name": existing_entity["name"],
            "entity_type": existing_entity["entity_type"],
            "attributes": merged_attributes,
            "tenant_id": tenant_id,
            "cell_id": cell_id,
            "updated_at": datetime.utcnow().isoformat()
        }
