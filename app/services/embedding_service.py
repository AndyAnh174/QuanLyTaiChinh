"""
Embedding service using Ollama bge-m3 model
"""
import requests
from typing import List
from django.conf import settings
from django.core.cache import cache
import hashlib
import json


class EmbeddingService:
    """
    Service for generating embeddings using Ollama bge-m3 model
    with Redis caching
    """
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_URL
        self.model_name = "bge-m3"  # bge-m3 embedding model
        self.cache_ttl = 86400 * 7  # 7 days cache
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Get embedding for text, with caching support
        
        Args:
            text: Text to embed
            use_cache: Whether to use cache
        
        Returns:
            Embedding vector (list of floats)
        """
        if use_cache:
            # Check cache first
            cache_key = self._get_cache_key(text)
            cached_embedding = cache.get(cache_key)
            if cached_embedding:
                return cached_embedding
        
        # Generate embedding
        embedding = self._generate_embedding(text)
        
        # Cache result
        if use_cache:
            cache.set(cache_key, embedding, self.cache_ttl)
        
        return embedding
    
    def get_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Get embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cache
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        if use_cache:
            # Check cache for each text
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                cached = cache.get(cache_key)
                if cached:
                    embeddings.append((i, cached))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                # Ollama embeddings API
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.model_name,
                        "prompt": uncached_texts[0] if len(uncached_texts) == 1 else uncached_texts
                    },
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                # Handle single or batch response
                if isinstance(result, list):
                    new_embeddings = [item.get("embedding", []) for item in result]
                else:
                    new_embeddings = [result.get("embedding", [])]
                
                # Cache new embeddings
                if use_cache:
                    for text, embedding in zip(uncached_texts, new_embeddings):
                        cache_key = self._get_cache_key(text)
                        cache.set(cache_key, embedding, self.cache_ttl)
                
                # Combine cached and new embeddings
                for idx, emb in zip(uncached_indices, new_embeddings):
                    embeddings.append((idx, emb))
            except Exception as e:
                print(f"Error generating embeddings: {e}")
                # Fallback: return empty embeddings
                for idx in uncached_indices:
                    embeddings.append((idx, [0.0] * 768))  # Default size for bge-m3
        
        # Sort by index and return just embeddings
        embeddings.sort(key=lambda x: x[0])
        return [emb for _, emb in embeddings]
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768  # bge-m3 produces 768-dimensional vectors
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"embedding:{self.model_name}:{text_hash}"


# Singleton instance
embedding_service = EmbeddingService()

