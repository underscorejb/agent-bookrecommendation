import json
import sys
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.data_ingestion_service.config.apis import OPEN_LIBRARY

def get_retry_session():
    """Creates a requests session with automatic retry logic."""
    session = requests.Session()
    # Retry strategy: 
    # - total=3: Try 3 times
    # - backoff_factor=1: Wait 1s, 2s, 4s between retries
    # - status_forcelist: Retry on these server error codes
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def fetch_subject_data(subject: str, limit: int = 25, http_get=None) -> dict:
    """Fetch raw subject data from Open Library API."""
    # Use the retry session if no custom http_get is provided (standard run)
    if http_get is None:
        session = get_retry_session()
        http_get = session.get

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
                "cover_i": work.get("cover_id") # Subject API uses cover_id, Search API uses cover_i
            }
            for work in data.get("works", [])
            if work.get("title")
        ]
    }

def get_subject(subject: str, limit: int = 25, http_get=None) -> dict:
    """Main method: fetches API data, transforms it, and saves to books.json."""
    raw_data = fetch_subject_data(subject, limit, http_get=http_get)
    simplified_data = transform_to_books_format(raw_data, subject)

    output_path = Path(__file__).parent.joinpath("books.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(
        json.dumps(simplified_data, indent=2), encoding="utf-8"
    )

    return simplified_data

if __name__ == "__main__":
    try:
        genre_arg = sys.argv[1] if len(sys.argv) > 1 else "mystery"
        result = get_subject(genre_arg)
        print(json.dumps(result))
    except requests.exceptions.RetryError:
        sys.stderr.write("Error: Maximum retries reached. The Open Library server is unavailable.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        sys.stderr.write("Error: The request timed out after multiple attempts.")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}")
        sys.exit(1)