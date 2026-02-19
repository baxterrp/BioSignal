from pydantic import BaseModel


class PubMedRawRecord(BaseModel):
    pmid: str
    title: str
    mesh_terms: list[str]
    authors: list[str]
    abstract: str | None = None
