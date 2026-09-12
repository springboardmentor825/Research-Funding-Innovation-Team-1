"""Hybrid retrieval index for the RAG assistant.

Pure-Python BM25 (Okapi) ranking over the platform's structured data:
  - Funding opportunities
  - The global 50K OpenAlex research corpus
  - Registered patents

The index is built lazily on first use and cached in-process with a TTL.
"""
import math
import re
import threading
import time
from typing import Dict, List, Tuple, Optional

from sqlalchemy.orm import Session

from app.models import FundingOpportunity, ResearchPublication, Patent

_STOP = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "of", "to", "in",
    "on", "at", "by", "for", "with", "from", "as", "is", "are", "was", "were", "be",
    "been", "this", "that", "these", "those", "what", "which", "who", "whom", "how",
    "show", "list", "tell", "find", "give", "some", "any", "all", "about", "please",
    "help", "can", "could", "would", "should", "will", "there", "their", "its", "it",
    "has", "have", "had", "do", "does", "did", "not", "no", "me", "my", "our", "us",
    "you", "your", "we", "they", "them", "here", "where", "why", "when", "also",
    "more", "most", "related", "available", "currently", "looking", "want", "need",
    "using", "based", "new", "recent", "research", "researcher",
}

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def tokenize(text: Optional[str]) -> List[str]:
    """Lowercase alphanumeric tokens, stopwords removed."""
    if not text:
        return []
    return [t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 1 and t not in _STOP]


class BM25Index:
    """Okapi BM25 over a static document store."""

    def __init__(self, docs: List[Tuple[int, str]]):
        # docs: (doc_id, text)
        self.k1 = 1.5
        self.b = 0.75
        self.doc_count = len(docs)
        self.doc_len: Dict[int, int] = {}
        self.postings: Dict[str, Dict[int, int]] = {}
        self.avgdl = 0.0
        self._build(docs)

    def _build(self, docs: List[Tuple[int, str]]):
        if not docs:
            self.avgdl = 0.0
            return
        total = 0
        for doc_id, text in docs:
            tokens = tokenize(text)
            self.doc_len[doc_id] = len(tokens)
            total += len(tokens)
            freq: Dict[str, int] = {}
            for tok in tokens:
                freq[tok] = freq.get(tok, 0) + 1
            for tok, f in freq.items():
                self.postings.setdefault(tok, {})[doc_id] = f
        self.avgdl = total / self.doc_count

    def score(self, query_tokens: List[str], doc_id: int) -> float:
        if self.avgdl <= 0 or not query_tokens:
            return 0.0
        dl = self.doc_len.get(doc_id, 0)
        score = 0.0
        for tok in query_tokens:
            post = self.postings.get(tok)
            if not post or doc_id not in post:
                continue
            tf = post[doc_id]
            n = len(post)
            idf = math.log(1 + (self.doc_count - n + 0.5) / (n + 0.5))
            denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += idf * (tf * (self.k1 + 1)) / denom
        return score

    def search(self, query_tokens: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        if not query_tokens or not self.doc_count:
            return []
        # Only candidate ids that hit at least one query token
        candidates: Dict[int, float] = {}
        for tok in query_tokens:
            for doc_id in self.postings.get(tok, {}):
                candidates[doc_id] = 0.0
        for doc_id in candidates:
            candidates[doc_id] = self.score(query_tokens, doc_id)
        ranked = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


class RetrievalCorpus:
    """In-process cached indexes for funding, research corpus, and patents."""

    def __init__(self):
        self._lock = threading.Lock()
        self._ttl = 300.0  # rebuild every 5 minutes
        self._built_at = 0.0

        # Funding index
        self._fund_docs: List[Tuple[int, str]] = []
        self._fund_index: Optional[BM25Index] = None
        self._fund_meta: Dict[int, dict] = {}

        # Research corpus
        self._pub_docs: List[Tuple[int, str]] = []
        self._pub_index: Optional[BM25Index] = None
        self._pub_meta: Dict[int, dict] = {}

        # Patents
        self._pat_docs: List[Tuple[int, str]] = []
        self._pat_index: Optional[BM25Index] = None
        self._pat_meta: Dict[int, dict] = {}


_corpus = RetrievalCorpus()


def _ensure_built(db: Session) -> RetrievalCorpus:
    """Build indexes if stale, under lock."""
    global _corpus
    if _corpus._built_at and (time.time() - _corpus._built_at) < _corpus._ttl:
        return _corpus
    with _corpus._lock:
        if _corpus._built_at and (time.time() - _corpus._built_at) < _corpus._ttl:
            return _corpus

        # Funding
        open_opps = db.query(FundingOpportunity).filter(FundingOpportunity.status == "open").all()
        _corpus._fund_docs = []
        _corpus._fund_meta = {}
        for opp in open_opps:
            text = " ".join(filter(None, [
                opp.title, opp.funder, opp.description, opp.research_domains,
                opp.technology_areas, opp.keywords, opp.match_badges, opp.eligibility,
            ]))
            _corpus._fund_docs.append((opp.id, text))
            _corpus._fund_meta[opp.id] = {
                "title": opp.title, "funder": opp.funder, "amount_range": opp.amount_range,
                "deadline": str(opp.deadline) if opp.deadline else None,
                "description": opp.description, "research_domains": opp.research_domains,
                "technology_areas": opp.technology_areas, "semantic_fit": opp.semantic_fit,
            }
        _corpus._fund_index = BM25Index(_corpus._fund_docs)

        # Global research corpus
        pubs = db.query(ResearchPublication).all()
        _corpus._pub_docs = []
        _corpus._pub_meta = {}
        for p in pubs:
            text = " ".join(filter(None, [
                p.title, p.primary_topic, p.topics_raw, p.concepts_raw, p.authors_raw,
                p.source or "",
            ]))
            _corpus._pub_docs.append((p.research_id, text))
            _corpus._pub_meta[p.research_id] = {
                "title": p.title, "year": p.publication_year, "source": p.source,
                "authors": p.authors_raw, "cited_by_count": p.cited_by_count,
                "doi": p.doi, "primary_topic": p.primary_topic,
            }
        _corpus._pub_index = BM25Index(_corpus._pub_docs)

        # Patents (user-registered & global demo assets)
        pats = db.query(Patent).all()
        _corpus._pat_docs = []
        _corpus._pat_meta = {}
        for pt in pats:
            text = " ".join(filter(None, [
                pt.title, pt.technology_domain, pt.inventor, pt.assignee,
                pt.filing_date.strftime("%Y") if pt.filing_date else None,
            ]))
            _corpus._pat_docs.append((pt.patent_id, text))
            _corpus._pat_meta[pt.patent_id] = {
                "title": pt.title, "technology_domain": pt.technology_domain,
                "inventor": pt.inventor, "assignee": pt.assignee,
                "filing_date": str(pt.filing_date) if pt.filing_date else None,
            }
        _corpus._pat_index = BM25Index(_corpus._pat_docs)

        _corpus._built_at = time.time()
        return _corpus


def retrieve_funding(query: str, db: Session, top_k: int = 5) -> List[Dict]:
    corpus = _ensure_built(db)
    if not corpus._fund_index or not corpus._fund_index.doc_count:
        return []
    tokens = tokenize(query)
    hits = corpus._fund_index.search(tokens, top_k)
    results = []
    for doc_id, score in hits:
        meta = corpus._fund_meta[doc_id]
        results.append({"type": "funding_opportunity", "id": doc_id, "score": round(score, 2), **meta})
    return results


def retrieve_publications(query: str, db: Session, top_k: int = 5) -> List[Dict]:
    corpus = _ensure_built(db)
    if not corpus._pub_index or not corpus._pub_index.doc_count:
        return []
    tokens = tokenize(query)
    hits = corpus._pub_index.search(tokens, top_k)
    results = []
    for doc_id, score in hits:
        meta = corpus._pub_meta[doc_id]
        results.append({"type": "publication", "id": doc_id, "score": round(score, 2), **meta})
    return results


def retrieve_patents(query: str, db: Session, top_k: int = 5) -> List[Dict]:
    corpus = _ensure_built(db)
    if not corpus._pat_index or not corpus._pat_index.doc_count:
        return []
    tokens = tokenize(query)
    hits = corpus._pat_index.search(tokens, top_k)
    results = []
    for doc_id, score in hits:
        meta = corpus._pat_meta[doc_id]
        results.append({"type": "patent", "id": doc_id, "score": round(score, 2), **meta})
    return results