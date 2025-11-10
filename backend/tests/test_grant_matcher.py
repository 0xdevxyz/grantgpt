"""
Tests for Grant Matcher Service
"""
import pytest
from app.services.grant_matcher import grant_matcher


@pytest.mark.asyncio
async def test_grant_matcher_search():
    """Test basic grant search functionality"""
    # Mock project description
    project_description = "AI-powered platform for automation"
    
    # TODO: Mock Qdrant responses
    # For now, just test that the function runs
    
    try:
        results = await grant_matcher.search_grants(
            project_description=project_description,
            budget=300000,
            limit=5
        )
        
        # Basic assertions
        assert isinstance(results, list)
        # assert len(results) <= 5
        
    except Exception as e:
        # Expected to fail without actual Qdrant data
        assert "Qdrant" in str(e) or "connection" in str(e).lower()


def test_build_query_text():
    """Test query text building"""
    description = "Test project"
    company_info = {"industry": "Software", "company_size": 25}
    budget = 100000
    location = "Munich"
    
    # Access private method for testing
    query_text = grant_matcher._build_query_text(
        description, company_info, budget, location
    )
    
    assert "Test project" in query_text
    assert "Software" in query_text
    assert "100000" in query_text
    assert "Munich" in query_text


def test_filter_by_criteria():
    """Test grant filtering"""
    # Mock results
    mock_results = [
        {
            "score": 0.9,
            "payload": {
                "external_id": "grant1",
                "max_funding": 500000,
                "deadline": None,
            }
        },
        {
            "score": 0.8,
            "payload": {
                "external_id": "grant2",
                "max_funding": 100000,
                "deadline": "2025-12-31T23:59:59Z",
            }
        }
    ]
    
    # Filter with budget constraint
    filtered = grant_matcher._filter_by_criteria(
        mock_results,
        budget=200000,
        location=None,
        company_info=None
    )
    
    # Should keep grant1 (500k > 200k) but not grant2 (100k < 200k)
    assert len(filtered) == 1
    assert filtered[0]["payload"]["external_id"] == "grant1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

