import asyncio

import httpx

from biosignal.core.config import settings


class PubMedFetcher:
    def __init__(self) -> None:
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_requests)

    async def search(self, query: str, max_results: int = 100) -> list[str]:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": str(max_results),
            "retmode": "json",
            "api_key": settings.ncbi_api_key,
        }

        async with self._semaphore, httpx.AsyncClient() as pubMedHttpClient:
            response = await pubMedHttpClient.get(
                f"{settings.pubmed_base_url}/esearch.fcgi", params=params
            )
            response.raise_for_status()  # Check for HTTP errors
            return response.json()["esearchresult"]["idlist"]  # Extract PMIDs from the response
