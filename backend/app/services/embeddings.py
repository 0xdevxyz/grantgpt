"""
Embedding Service for text-to-vector conversion using OpenRouter
"""
from typing import List
from app.core.config import settings
from app.services.openrouter_client import openrouter_client


class EmbeddingService:
    """Service for generating embeddings via OpenRouter"""
    
    def __init__(self):
        self.dimensions = 3072  # OpenAI text-embedding-3-large full dimensions
        self.client = openrouter_client
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            return await self.client.create_embedding(text)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                embedding = await self.embed_text(text)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error embedding text: {e}")
                raise
        return embeddings


# Singleton instance
embedding_service = EmbeddingService()

