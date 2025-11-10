"""
Grant Matching Service - AI-powered grant recommendation
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service


class GrantMatcher:
    """Service for matching user projects with suitable grants"""
    
    async def search_grants(
        self,
        project_description: str,
        company_info: Optional[Dict[str, Any]] = None,
        budget: Optional[float] = None,
        location: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find best matching grants for a project
        
        Args:
            project_description: User's project description
            company_info: Company details (size, industry, etc.)
            budget: Project budget in EUR
            location: Company location (for regional grants)
            limit: Number of results to return
            
        Returns:
            List of matching grants with match scores
        """
        # 1. Generate embedding for project description
        query_text = self._build_query_text(
            project_description,
            company_info,
            budget,
            location
        )
        query_vector = await embedding_service.embed_text(query_text)
        
        # 2. Search in Qdrant
        # Get more results for post-processing
        raw_results = qdrant_service.search_similar_grants(
            query_vector=query_vector,
            limit=limit * 5,
            score_threshold=0.5
        )
        
        # 3. Post-processing: filter and rank
        filtered_results = self._filter_by_criteria(
            raw_results,
            budget=budget,
            location=location,
            company_info=company_info
        )
        
        # 4. Rank by multiple factors
        ranked_results = self._rank_grants(filtered_results)
        
        # 5. Return top N
        return ranked_results[:limit]
    
    def _build_query_text(
        self,
        description: str,
        company_info: Optional[Dict[str, Any]],
        budget: Optional[float],
        location: Optional[str]
    ) -> str:
        """Build comprehensive query text for embedding"""
        parts = [description]
        
        if company_info:
            if "industry" in company_info:
                parts.append(f"Industry: {company_info['industry']}")
            if "company_size" in company_info:
                parts.append(f"Company size: {company_info['company_size']} employees")
        
        if budget:
            parts.append(f"Budget: {budget} EUR")
        
        if location:
            parts.append(f"Location: {location}")
        
        return " ".join(parts)
    
    def _filter_by_criteria(
        self,
        results: List[Dict[str, Any]],
        budget: Optional[float],
        location: Optional[str],
        company_info: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter grants by hard criteria"""
        filtered = []
        
        for result in results:
            payload = result["payload"]
            
            # Budget check
            if budget and "max_funding" in payload:
                if budget > payload["max_funding"]:
                    continue  # Project budget too high
            
            # Deadline check (skip expired grants)
            if "deadline" in payload and payload["deadline"]:
                try:
                    deadline = datetime.fromisoformat(payload["deadline"].replace("Z", "+00:00"))
                    if deadline < datetime.now(deadline.tzinfo):
                        continue  # Deadline passed
                except:
                    pass  # Invalid date format, keep grant
            
            # TODO: Add more filters (location, company size, etc.)
            
            filtered.append(result)
        
        return filtered
    
    def _rank_grants(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank grants by multiple factors:
        - Similarity score (from Qdrant)
        - Historical success rate
        - Deadline urgency
        """
        for result in results:
            payload = result["payload"]
            score = result["score"]
            
            # Base score is similarity
            final_score = score
            
            # Boost by success rate
            if "historical_success_rate" in payload:
                success_rate = payload["historical_success_rate"]
                final_score *= (1 + success_rate * 0.5)  # Up to 50% boost
            
            # Boost by deadline urgency (grants with near deadlines)
            if "deadline" in payload and payload["deadline"] and not payload.get("is_continuous", False):
                try:
                    deadline = datetime.fromisoformat(payload["deadline"].replace("Z", "+00:00"))
                    days_until = (deadline - datetime.now(deadline.tzinfo)).days
                    if days_until < 30:
                        final_score *= 1.2  # 20% boost for urgent deadlines
                    elif days_until < 60:
                        final_score *= 1.1  # 10% boost
                except:
                    pass
            
            result["match_score"] = final_score
        
        # Sort by final score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return results


# Singleton instance
grant_matcher = GrantMatcher()

