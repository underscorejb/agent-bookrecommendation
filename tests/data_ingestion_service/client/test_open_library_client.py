# tests/data_ingestion_service/client/test_open_library_client.py
import pytest
import json
from pathlib import Path
from unittest.mock import Mock
from requests.exceptions import HTTPError
from src.data_ingestion_service.client.open_library_client import get_subject

@pytest.mark.api_client
class TestOpenLibraryClient:
        
    def test_get_subject_200():
        """Test a successful 200 response with one work."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "key": "/subjects/fantasy",
            "name": "fantasy",
            "works": [
                {
                    "key": "/works/OL12345W",
                    "title": "The Hobbit",
                    "authors": [{"name": "J.R.R. Tolkien"}],
                    "first_publish_year": 1937
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_subject("fantasy", limit=1, http_get=mock_get)

        assert result["key"] == "/subjects/fantasy"
        assert result["name"] == "fantasy"
        assert isinstance(result["works"], list)
        work = result["works"][0]
        assert "key" in work
        assert "title" in work
        assert "authors" in work
        assert isinstance(work["authors"], list)
        assert "first_publish_year" in work


    def test_get_subject_multiple_works():
        """Test response with multiple works."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "key": "/subjects/mystery",
            "name": "mystery",
            "works": [
                {"key": "/works/OL1W", "title": "Book One", "authors": [{"name": "Author A"}], "first_publish_year": 2001},
                {"key": "/works/OL2W", "title": "Book Two", "authors": [{"name": "Author B"}], "first_publish_year": 2002},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_subject("mystery", http_get=mock_get)
        assert len(result["works"]) == 2
        for work in result["works"]:
            assert "title" in work
            assert "authors" in work


    def test_get_subject_empty_works():
        """Test response with empty works list."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"key": "/subjects/fantasy", "name": "fantasy", "works": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_subject("fantasy", http_get=mock_get)
        assert result["works"] == []


    def test_get_subject_no_authors():
        """Test work with no authors."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "key": "/subjects/fantasy",
            "name": "fantasy",
            "works": [{"key": "/works/OL12345W", "title": "The Hobbit", "authors": [], "first_publish_year": 1937}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_subject("fantasy", http_get=mock_get)
        work = result["works"][0]
        assert work["authors"] == []


    def test_get_subject_4xx_raises():
        """Test that a 4xx status code raises HTTPError."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Client Error")
        mock_get.return_value = mock_response

        with pytest.raises(HTTPError):
            get_subject("unknown-genre", http_get=mock_get)


    def test_get_subject_5xx_raises():
        """Test that a 5xx status code raises HTTPError."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(HTTPError):
            get_subject("fantasy", http_get=mock_get)


    def test_get_subject_params_passed_correctly():
        """Test that the correct URL and query params are passed to http_get."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"works": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        genre = "mystery"
        limit = 5
        get_subject(genre, limit=limit, http_get=mock_get)

        url_called = mock_get.call_args[0][0]  # first positional argument is URL
        params_called = mock_get.call_args[1]["params"]

        expected_url = f"https://openlibrary.org/subjects/{genre}.json"  # adjust base_url if needed
        assert url_called == expected_url
        assert params_called["limit"] == limit


    def test_get_subject_default_limit():
        """Test that default limit is 25 if not specified."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"works": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        get_subject("fantasy", http_get=mock_get)
        params_called = mock_get.call_args[1]["params"]
        assert params_called["limit"] == 25


    def test_get_subject_json_body_format():
        """Test that the returned JSON matches expected Open Library response structure."""
        mock_get = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "key": "/subjects/mystery",
            "name": "mystery",
            "works": [
                {
                    "key": "/works/OL81592W",
                    "title": "Murder on the Orient Express",
                    "authors": [{"name": "Agatha Christie"}],
                    "first_publish_year": 1934
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_subject("mystery", http_get=mock_get)
        assert "key" in result
        assert "name" in result
        assert "works" in result
        assert isinstance(result["works"], list)
        work = result["works"][0]
        assert "key" in work
        assert "title" in work
        assert "authors" in work
        assert isinstance(work["authors"], list)
        assert "first_publish_year" in work

@pytest.mark.api_integration
class TestOpenLibraryClientIntegration:
    def test_save_subject_json(self):
        """Call the real Open Library API and save JSON response to a file."""
        subject = "science_fiction"
        limit = 5

        # Call the real API
        result = get_subject(subject, limit=limit)

        # Get path of the current test file
        test_file_path = Path(__file__).parent
        output_file = test_file_path / f"{subject}_response.json"

        # Save JSON
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)

        # Assertions
        assert "key" in result
        assert "name" in result
        assert isinstance(result.get("works", []), list)

        print(f"Saved JSON response to {output_file}")
