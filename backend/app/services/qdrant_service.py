"""
Qdrant Vector Database Service for grant storage and similarity search
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import uuid

from app.core.config import settings


class QdrantService:
    """Service for interacting with Qdrant vector database"""
    
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = 3072  # OpenAI text-embedding-3-large (full dimensions)
    
    def ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            raise
    
    def upsert_grant(
        self,
        grant_id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ):
        """
        Insert or update a grant in the vector database
        
        Args:
            grant_id: Unique grant identifier
            vector: Embedding vector
            payload: Metadata (grant details)
        """
        try:
            point = PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, grant_id)),
                vector=vector,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"Error upserting grant {grant_id}: {e}")
            raise
    
    def search_similar_grants(
        self,
        query_vector: List[float],
        limit: int = 100,
        score_threshold: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar grants using vector similarity
        
        Args:
            query_vector: Query embedding
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filters: Optional filters (e.g., {"type": "federal"})
            
        Returns:
            List of matching grants with scores
        """
        try:
            # Build filters if provided
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter
            )
            
            # Format results
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error searching grants: {e}")
            raise
    
    def delete_grant(self, grant_id: str):
        """Delete a grant from the vector database"""
        try:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, grant_id))
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
        except Exception as e:
            print(f"Error deleting grant {grant_id}: {e}")
            raise
    
    def search_grants_by_filter(
        self,
        filter_conditions: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search grants by exact filter conditions (no vector search)
        
        Args:
            filter_conditions: Dictionary of field-value pairs to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching grants
        """
        try:
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            
            query_filter = Filter(must=conditions) if conditions else None
            
            # Use scroll to get points with filter
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            return [
                {
                    "id": result.id,
                    "payload": result.payload,
                    "score": 1.0  # No similarity score for filter-only search
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error searching grants by filter: {e}")
            raise
    
    def scroll_grants(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Scroll through grants with optional filtering and pagination
        
        Args:
            filter_conditions: Optional dictionary of filter conditions
            limit: Number of results per page
            offset: Offset for pagination
            
        Returns:
            List of grants
        """
        try:
            # Build filter
            query_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Scroll with offset
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            return [
                {
                    "id": result.id,
                    "payload": result.payload
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error scrolling grants: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "total_points": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            raise


# Singleton instance
qdrant_service = QdrantService()

