import pytest
import json
import os
import requests
from pathlib import Path
from unittest.mock import Mock, patch
from requests.exceptions import HTTPError, Timeout
from src.data_ingestion_service.client.open_library_client import (
    get_subject,
    fetch_subject_data,
    transform_to_books_format,
)

@pytest.mark.api_client
class TestOpenLibraryClient:

    def test_transform_missing_authors_key(self):
        """EDGE CASE: 'authors' key is missing entirely from a work."""
        raw_data = {
            "works": [{"title": "Ghost Book", "first_publish_year": 2024}] 
        }
        simplified = transform_to_books_format(raw_data, subject="horror")
        assert simplified["books"][0]["author"] is None

    def test_transform_with_cover_id(self):
        """NEW: Verify cover_id is correctly mapped to the simplified format."""
        raw_data = {
            "works": [{"title": "Cover Book", "authors": [], "cover_id": 12345}]
        }
        simplified = transform_to_books_format(raw_data, subject="art")
        assert simplified["books"][0]["cover_i"] == 12345

    def test_fetch_subject_data_timeout(self):
        """EDGE CASE: Verify timeout handling (simulating slow API)."""
        mock_get = Mock(side_effect=Timeout("API Connection Timed Out"))
        with pytest.raises(Timeout):
            fetch_subject_data("mystery", http_get=mock_get)

    def test_get_subject_filesystem_write(self, tmp_path):
        """Verify that get_subject actually writes to the disk."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"works": [{"title": "Saved Book", "authors": []}]}
        mock_get.return_value = mock_response

        test_json_path = tmp_path / "books.json"
        
        with patch("src.data_ingestion_service.client.open_library_client.Path") as mock_path:
            # We mock the path behavior to write to our temp test file
            mock_path.return_value.parent.joinpath.return_value = test_json_path
            
            get_subject("mystery", http_get=mock_get)
            
            assert test_json_path.exists()
            content = json.loads(test_json_path.read_text())
            assert content["books"][0]["title"] == "Saved Book"

@pytest.mark.api_integration
class TestOpenLibraryClientIntegration:

    def test_real_api_empty_subject(self):
        """
        Integration: What happens if a subject has zero results?
        RESOLVED: Added 503/504 error handling to skip test if Open Library is down.
        """
        try:
            result = get_subject("this_subject_should_never_exist_12345")
            assert "books" in result
            assert result["books"] == []
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            # Check if it's a server-side error (503 Service Unavailable)
            if hasattr(e.response, 'status_code') and e.response.status_code in [502, 503, 504]:
                pytest.skip(f"External API is down (Status {e.response.status_code}). Skipping integration test.")
            else:
                raise e