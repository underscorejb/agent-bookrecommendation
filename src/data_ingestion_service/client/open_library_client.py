# src/data_ingestion_service/client/open_library_client.py
import json
from pathlib import Path
import requests
from src.data_ingestion_service.config.apis import OPEN_LIBRARY


def fetch_subject_data(subject: str, limit: int = 25, http_get=requests.get) -> dict:
    """Fetch raw subject data from Open Library API."""
    response = http_get(
        f"{OPEN_LIBRARY['base_url']}/subjects/{subject}.json",
        headers=OPEN_LIBRARY["headers"],
        params={"limit": limit},
        timeout=OPEN_LIBRARY["timeout"],
    )
    response.raise_for_status()
    return response.json()


def transform_to_books_format(data: dict, subject: str) -> dict:
    """Convert raw API response into simplified books format."""
    return {
        "books": [
            {
                "title": work.get("title"),
                "author": (work.get("authors") or [{}])[0].get("name"),
                "first_publish_year": work.get("first_publish_year"),
                "subject": subject,
            }
            for work in data.get("works", [])
            if work.get("title")
        ]
    }


def get_subject(subject: str, limit: int = 25) -> dict:
    """
    Main method: fetches API data, transforms it, and saves to books.json.
    """
    simplified_data = transform_to_books_format(fetch_subject_data(subject, limit), subject)

    # Save to books.json next to this script
    Path(__file__).parent.joinpath("books.json").write_text(
        json.dumps(simplified_data, indent=2), encoding="utf-8"
    )

    return simplified_data
