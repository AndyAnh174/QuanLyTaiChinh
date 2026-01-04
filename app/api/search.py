"""
Semantic Search API endpoints
"""
from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from django.core.cache import cache
from ..qdrant_client import get_qdrant_service
from ..services.embedding_service import embedding_service

router = Router(tags=["search"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    score_threshold: Optional[float] = 0.5


class SearchResult(BaseModel):
    transaction_id: int
    score: float
    description: str
    category: Optional[str]
    amount: float
    date: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total: int


@router.post("/semantic", response=SearchResponse, summary="Semantic Search")
def semantic_search(request, data: SearchRequest):
    """
    Search transactions using semantic similarity.
    Converts query to embedding and searches Qdrant.
    """
    # Check cache first
    cache_key = f"search:{hash(data.query)}:{data.limit}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        # Generate embedding for query
        query_embedding = embedding_service.get_embedding(data.query)
        
        # Search Qdrant
        qdrant_service = get_qdrant_service()
        results = qdrant_service.search(
            query_vector=query_embedding,
            limit=data.limit,
            score_threshold=data.score_threshold
        )
        
        # Format results
        search_results = []
        for result in results:
            payload = result.get('payload', {})
            search_results.append(SearchResult(
                transaction_id=payload.get('transaction_id', 0),
                score=result.get('score', 0.0),
                description=payload.get('description', ''),
                category=payload.get('category'),
                amount=payload.get('amount', 0.0),
                date=payload.get('date', ''),
            ))
        
        response = SearchResponse(
            results=search_results,
            query=data.query,
            total=len(search_results)
        )
        
        # Cache result for 5 minutes
        cache.set(cache_key, response.dict(), 300)
        
        return response
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return SearchResponse(
            results=[],
            query=data.query,
            total=0
        )

