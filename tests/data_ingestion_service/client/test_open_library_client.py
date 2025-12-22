# # tests/data_ingestion_service/client/test_open_library_client.py
# import pytest
# import json
# from pathlib import Path
# from unittest.mock import Mock
# from requests.exceptions import HTTPError
# from src.data_ingestion_service.client.open_library_client import (
#     get_subject,
#     fetch_subject_data,
#     transform_to_books_format,
# )

# @pytest.mark.api_client
# class TestOpenLibraryClient:

#     def test_fetch_subject_data_success(self):
#         """Test that fetch_subject_data returns correct raw JSON."""
#         mock_get = Mock()
#         mock_response = Mock()
#         mock_response.json.return_value = {"works": [{"title": "Book A", "authors": [{"name": "Author A"}]}]}
#         mock_response.raise_for_status.return_value = None
#         mock_get.return_value = mock_response

#         data = fetch_subject_data("fantasy", http_get=mock_get)
#         assert "works" in data
#         assert data["works"][0]["title"] == "Book A"

#     def test_transform_to_books_format_basic(self):
#         """Test transformation converts raw data to simplified books format."""
#         raw_data = {
#             "works": [
#                 {"title": "Book A", "authors": [{"name": "Author A"}], "first_publish_year": 2000},
#                 {"title": "Book B", "authors": [], "first_publish_year": 2010},
#                 {"title": None, "authors": [{"name": "Author C"}], "first_publish_year": 2020},  # should be skipped
#             ]
#         }
#         simplified = transform_to_books_format(raw_data, subject="fantasy")
#         books = simplified["books"]

#         assert len(books) == 2
#         assert books[0] == {
#             "title": "Book A",
#             "author": "Author A",
#             "first_publish_year": 2000,
#             "subject": "fantasy",
#         }
#         assert books[1]["author"] is None  # empty authors handled gracefully

#     def test_get_subject_calls_api_and_transforms(self):
#         """Test get_subject integrates fetch and transform, returns simplified format."""
#         mock_get = Mock()
#         mock_response = Mock()
#         mock_response.json.return_value = {
#             "works": [{"title": "Book X", "authors": [{"name": "Author X"}], "first_publish_year": 1999}]
#         }
#         mock_response.raise_for_status.return_value = None
#         mock_get.return_value = mock_response

#         result = get_subject("mystery", limit=1, http_get=mock_get)
#         assert "books" in result
#         book = result["books"][0]
#         assert book["title"] == "Book X"
#         assert book["author"] == "Author X"
#         assert book["first_publish_year"] == 1999
#         assert book["subject"] == "mystery"

#     @pytest.mark.parametrize("http_error", [HTTPError("404 Client Error"), HTTPError("500 Server Error")])
#     def test_get_subject_raises_http_error(self, http_error):
#         """Test that get_subject raises HTTPError for 4xx and 5xx responses."""
#         mock_get = Mock()
#         mock_response = Mock()
#         mock_response.raise_for_status.side_effect = http_error
#         mock_get.return_value = mock_response

#         with pytest.raises(HTTPError):
#             get_subject("fantasy", http_get=mock_get)

#     def test_default_limit_used(self):
#         """Test that default limit of 25 is passed to API."""
#         mock_get = Mock()
#         mock_response = Mock()
#         mock_response.json.return_value = {"works": []}
#         mock_response.raise_for_status.return_value = None
#         mock_get.return_value = mock_response

#         get_subject("fantasy", http_get=mock_get)
#         params = mock_get.call_args[1]["params"]
#         assert params["limit"] == 25

#     def test_api_called_with_correct_url(self):
#         """Ensure API is called with correct subject URL."""
#         mock_get = Mock()
#         mock_response = Mock()
#         mock_response.json.return_value = {"works": []}
#         mock_response.raise_for_status.return_value = None
#         mock_get.return_value = mock_response

#         subject = "science_fiction"
#         get_subject(subject, limit=5, http_get=mock_get)
#         url_called = mock_get.call_args[0][0]
#         expected_url = f"https://openlibrary.org/subjects/{subject}.json"
#         assert url_called == expected_url

# @pytest.mark.api_integration
# class TestOpenLibraryClientIntegration:

#     def test_save_subject_books_json(self, tmp_path):
#         """
#         Integration test: fetch real API data, transform to books.json, save to temp folder,
#         and validate structure.
#         """
#         subject = "mystery"
#         limit = 3

#         # Call real API
#         result = get_subject(subject, limit=limit)

#         # Save to temporary path
#         output_file = tmp_path / "books.json"
#         output_file.write_text(json.dumps(result, indent=2), encoding="utf-8")

#         # Load back and verify structure
#         saved = json.loads(output_file.read_text())
#         assert "books" in saved
#         assert isinstance(saved["books"], list)
#         for book in saved["books"]:
#             assert "title" in book
#             assert "author" in book
#             assert "first_publish_year" in book
#             assert book["subject"] == subject
