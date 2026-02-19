import asyncio
import xml.etree.ElementTree as ET

import httpx

from biosignal.core.config import settings
from biosignal.models.paper import PubMedRawRecord


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

    async def fetch_records(self, pmids: list[str]) -> list[PubMedRawRecord]:
        results = []

        for i in range(0, len(pmids), 100):
            batch = pmids[i : i + 100]
            records = await self._fetch_batch(batch)
            results.extend(records)

        return results

    async def _fetch_batch(self, pmids: list[str]) -> list[PubMedRawRecord]:
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract",
            "api_key": settings.ncbi_api_key,
        }

        async with self._semaphore, httpx.AsyncClient() as pubMedHttpClient:
            response = await pubMedHttpClient.get(
                f"{settings.pubmed_base_url}/efetch.fcgi", params=params
            )
            response.raise_for_status()  # Check for HTTP errors
            return self._parse_xml(response.text)

    def _parse_xml(self, xml_text: str) -> list[PubMedRawRecord]:
        root = ET.fromstring(xml_text)
        records: list[PubMedRawRecord] = []

        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID", default="")
            title = article.findtext(".//ArticleTitle", default="")
            abstract = article.findtext(".//AbstractText", default="")
            authors = [
                f"{a.findtext('LastName', '')} {a.findtext('Initials', '')}".strip()
                for a in article.findall(".//Author")
            ]
            mesh = [m.findtext("DescriptorName", "") for m in article.findall(".//MeshHeading")]

            records.append(
                PubMedRawRecord(
                    pmid=pmid, title=title, abstract=abstract, authors=authors, mesh_terms=mesh
                )
            )

        return records
