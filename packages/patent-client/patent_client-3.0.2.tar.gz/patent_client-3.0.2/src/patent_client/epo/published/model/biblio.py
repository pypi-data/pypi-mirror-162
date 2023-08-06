from dataclasses import dataclass
from dataclasses import field
from typing import List

from patent_client.epo.number_service.model import DocumentId
from patent_client.epo.util import InpadocModel
from patent_client.util import Model


@dataclass
class Citation(InpadocModel):
    cited_phase: str = None
    cited_by: str = None
    epodoc: DocumentId = None
    docdb: DocumentId = None
    original: DocumentId = None

    def __repr__(self):
        return f"Citation(doc_number={str(self.docdb)}, cited_by={self.cited_by}, cited_phase={self.cited_phase})"

    @property
    def docdb_number(self):
        return str(self.docdb)


@dataclass
class Title(Model):
    lang: str
    text: str

    def __repr__(self):
        return f"Title(lang={self.lang}, text={self.text})"


def limit_text(string, limit=30):
    if len(string) < limit:
        return string
    else:
        return f"{string[:limit]}..."


@dataclass
class InpadocBiblio(InpadocModel):
    __manager__ = "patent_client.epo.published.manager.BiblioManager"
    country: str = None
    doc_number: str = None
    kind: str = None
    family_id: str = None
    publication_number: str = None
    application_number: str = None
    publication_reference_docdb: DocumentId = None
    publication_reference_epodoc: DocumentId = None
    publication_reference_original: DocumentId = None
    application_reference_docdb: DocumentId = None
    application_reference_epodoc: DocumentId = None
    application_reference_original: DocumentId = None
    intl_class: List[str] = field(default_factory=list)
    cpc_class: List[str] = field(default_factory=list)
    us_class: List[str] = field(default_factory=list)
    priority_claims: List[str] = field(default_factory=list)
    title: str = None
    titles: List[Title] = field(default_factory=list)
    abstract: str = None
    citations: List[Citation] = field(default_factory=list)
    applicants_epodoc: List[str] = field(default_factory=list)
    applicants_original: List[str] = field(default_factory=list)
    inventors_epodoc: List[str] = field(default_factory=list)
    inventors_original: List[str] = field(default_factory=list)
    # TODO: NPL citations

    def __repr__(self):
        return f"InpadocBiblio(publication_number={self.publication_number}, title={limit_text(self.title, 30)})"

    @property
    def docdb_number(self):
        return str(self.publication_reference_docdb)


@dataclass
class BiblioResult(Model):
    documents: list = None
