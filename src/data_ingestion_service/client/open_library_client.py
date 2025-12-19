import requests
from src.data_ingestion_service.config.apis import OPEN_LIBRARY

def get_subject(subject: str, limit: int = 25, http_get=requests.get):
    url = f"{OPEN_LIBRARY['base_url']}/subjects/{subject}.json"
    params = {"limit": limit}

    response = http_get(
        url,
        headers=OPEN_LIBRARY["headers"],
        params=params,
        timeout=OPEN_LIBRARY["timeout"]
    )
    response.raise_for_status()
    return response.json()
