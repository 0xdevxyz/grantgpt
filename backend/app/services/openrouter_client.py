"""
OpenRouter Client - Alternative zu OpenAI mit mehr Modell-Optionen
"""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings


class OpenRouterClient:
    """Client für OpenRouter API"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.APP_NAME,
            "X-Title": settings.APP_NAME,
            "Content-Type": "application/json"
        }
        
        # Model Configuration
        self.chat_model = "anthropic/claude-3.5-sonnet"  # Bestes Modell für lange Texte
        self.embedding_model = "openai/text-embedding-3-large"  # OpenAI Embeddings via OpenRouter
        
        # Fallback wenn kein OpenRouter Key
        self.use_openai_fallback = not self.api_key or self.api_key == ""
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Chat Completion via OpenRouter
        
        Args:
            messages: Liste von {role: str, content: str}
            temperature: 0-1
            max_tokens: Max response tokens
            
        Returns:
            Generated text
        """
        if self.use_openai_fallback:
            return await self._openai_fallback_chat(messages, temperature, max_tokens)
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.chat_model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except Exception as e:
                print(f"OpenRouter error: {e}")
                raise
    
    async def create_embedding(
        self,
        text: str
    ) -> List[float]:
        """
        Create embedding via OpenRouter
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if self.use_openai_fallback:
            return await self._openai_fallback_embedding(text)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json={
                        "model": self.embedding_model,
                        "input": text
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
                
            except Exception as e:
                print(f"OpenRouter embedding error: {e}")
                raise
    
    async def _openai_fallback_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Fallback zu OpenAI wenn kein OpenRouter Key"""
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        
        response = await openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    async def _openai_fallback_embedding(self, text: str) -> List[float]:
        """Fallback zu OpenAI Embeddings"""
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        
        response = await openai.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding


# Singleton instance
openrouter_client = OpenRouterClient()

