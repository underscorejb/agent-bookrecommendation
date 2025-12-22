import json
import sys
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

# UPDATE: Added http_get=requests.get here to fix your test failure
def get_subject(subject: str, limit: int = 25, http_get=requests.get) -> dict:
    """Main method: fetches API data, transforms it, and saves to books.json."""
    
    # Pass the injected http_get down to the fetcher
    raw_data = fetch_subject_data(subject, limit, http_get=http_get)
    simplified_data = transform_to_books_format(raw_data, subject)

    # Save to books.json next to this script
    output_path = Path(__file__).parent.joinpath("books.json")
    
    # Ensure the directory exists (good practice for edge cases)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(
        json.dumps(simplified_data, indent=2), encoding="utf-8"
    )

    return simplified_data

if __name__ == "__main__":
    try:
        genre_arg = sys.argv[1] if len(sys.argv) > 1 else "mystery"
        # When running normally, it uses the default requests.get
        result = get_subject(genre_arg)
        print(json.dumps(result))
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)