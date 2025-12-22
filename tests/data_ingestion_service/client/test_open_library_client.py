# tests/data_ingestion_service/client/test_open_library_client.py
import pytest
import json
import os
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
            "works": [{"title": "Ghost Book", "first_publish_year": 2024}] # No authors key
        }
        simplified = transform_to_books_format(raw_data, subject="horror")
        assert simplified["books"][0]["author"] is None

    def test_transform_empty_authors_list(self):
        """EDGE CASE: 'authors' is an empty list."""
        raw_data = {
            "works": [{"title": "Anonymous", "authors": [], "first_publish_year": 1800}]
        }
        simplified = transform_to_books_format(raw_data, subject="history")
        assert simplified["books"][0]["author"] is None

    def test_transform_malformed_author_object(self):
        """EDGE CASE: Author object exists but doesn't have a 'name' key."""
        raw_data = {
            "works": [{"title": "Broken Author", "authors": [{"not_name": "Value"}]}]
        }
        simplified = transform_to_books_format(raw_data, subject="mystery")
        assert simplified["books"][0]["author"] is None

    def test_transform_skips_works_without_titles(self):
        """EDGE CASE: Verify works with missing titles are filtered out."""
        raw_data = {
            "works": [
                {"title": "Valid Book", "authors": []},
                {"authors": [{"name": "No Title Author"}]} # Missing title
            ]
        }
        simplified = transform_to_books_format(raw_data, "test")
        assert len(simplified["books"]) == 1
        assert simplified["books"][0]["title"] == "Valid Book"

    def test_fetch_subject_data_timeout(self):
        """EDGE CASE: Verify timeout handling (simulating slow API)."""
        mock_get = Mock(side_effect=Timeout("API Connection Timed Out"))
        with pytest.raises(Timeout):
            fetch_subject_data("mystery", http_get=mock_get)

    def test_get_subject_filesystem_write(self, tmp_path):
        """
        NEW: Verify that get_subject actually writes to the disk.
        We patch 'Path' to ensure it writes to our temp directory instead of actual src.
        """
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"works": [{"title": "Saved Book", "authors": []}]}
        mock_get.return_value = mock_response

        # We patch Path in the script to point to a temporary test file
        test_json_path = tmp_path / "books.json"
        
        with patch("src.data_ingestion_service.client.open_library_client.Path") as mock_path:
            # Setup the mock so Path(__file__).parent.joinpath("books.json") returns our temp path
            mock_path.return_value.parent.joinpath.return_value = test_json_path
            
            get_subject("mystery", http_get=mock_get)
            
            # Assert file was created and contains correct data
            assert test_json_path.exists()
            content = json.loads(test_json_path.read_text())
            assert content["books"][0]["title"] == "Saved Book"

@pytest.mark.api_integration
class TestOpenLibraryClientIntegration:

    def test_real_api_empty_subject(self):
        """Integration: What happens if a subject has zero results?"""
        # Using a very unlikely subject string
        result = get_subject("this_subject_should_never_exist_12345")
        assert "books" in result
        assert result["books"] == []