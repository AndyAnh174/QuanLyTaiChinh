"""
Qdrant Vector Database Client
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from django.conf import settings
import uuid
from typing import List, Optional, Dict, Any


class QdrantService:
    """Service class for Qdrant vector database operations"""
    
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            # Create collection with vector size 768 (for bge-m3 embedding)
            # Adjust vector_size based on your embedding model
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=768,  # bge-m3 embedding size
                    distance=Distance.COSINE
                )
            )
            print(f"Created Qdrant collection: {self.collection_name}")
    
    def upsert_points_batch(
        self,
        points: List[Dict[str, Any]]
    ) -> bool:
        """
        Batch upsert multiple points for better performance
        
        Args:
            points: List of dicts with 'id', 'vector', 'payload' keys
        
        Returns:
            bool: Success status
        """
        try:
            from qdrant_client.models import PointStruct
            point_structs = [
                PointStruct(
                    id=point['id'],
                    vector=point['vector'],
                    payload=point['payload']
                )
                for point in points
            ]
            self.client.upsert(
                collection_name=self.collection_name,
                points=point_structs
            )
            return True
        except Exception as e:
            print(f"Error batch upserting points to Qdrant: {e}")
            return False
    
    def upsert_point(
        self,
        point_id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ) -> bool:
        """
        Insert or update a point in Qdrant
        
        Args:
            point_id: Unique identifier (can use transaction.id)
            vector: Embedding vector
            payload: Metadata (description, category, amount, etc.)
        
        Returns:
            bool: Success status
        """
        try:
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
        except Exception as e:
            print(f"Error upserting point to Qdrant: {e}")
            return False
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            score_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of search results with payload
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return []
    
    def delete_point(self, point_id: str) -> bool:
        """Delete a point from Qdrant"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return True
        except Exception as e:
            print(f"Error deleting point from Qdrant: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            result = {
                "name": self.collection_name,
                "points_count": info.points_count,
            }
            # Try to get vectors count if available
            if hasattr(info, 'vectors_count'):
                result["vectors_count"] = info.vectors_count
            elif hasattr(info, 'config') and hasattr(info.config, 'params'):
                # Get vector size from config
                if hasattr(info.config.params, 'vectors'):
                    if hasattr(info.config.params.vectors, 'size'):
                        result["vector_size"] = info.config.params.vectors.size
            return result
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}


# Singleton instance (lazy initialization)
_qdrant_service = None

def get_qdrant_service():
    """Get or create Qdrant service instance (lazy initialization)"""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service

