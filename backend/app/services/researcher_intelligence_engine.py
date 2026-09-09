"""
=============================================================================
RESEARCHER INTELLIGENCE ENGINE — MEMBER 4 DELIVERABLE
=============================================================================
Milestone 3: Research Funding & Innovation Intelligence Platform

This module combines researcher profiles, publication records, and patent
filings into a structured researcher expertise/strength profile. It uses
TF-IDF cosine similarity for content-based matching (NOT name-based joins).

SCOPE LIMITATIONS (documented by design):
  - Patent dataset: 2010-only, Indian Patent Office filings only.
    No citation field available for patents.
    Compensated by: match count + status weighting
    (granted/published > pending > withdrawn/refused).
  - The 8 researchers do NOT literally appear as authors/inventors in
    the publication or patent datasets. All matching is content-based
    using keywords, research domains, topics, and concepts.
  - TF-IDF is chosen over sentence-transformers for lightweight,
    zero-download deployment. Both approaches are viable; TF-IDF is
    sufficient for keyword/topic-level matching at this scale.

INPUT DATASETS:
  1. researcher_profiles.json — 8 researcher profiles
  2. openalex_50000_clean.csv — ~50,000 publication records
  3. 2010_cleaned.csv — Indian Patent Office 2010 filings

OUTPUT:
  - researcher_intelligence.json — structured intelligence per researcher
  - In-memory dict for FastAPI consumption by Member 5's dashboard

Author: Member 4 (Researcher Intelligence)
=============================================================================
"""

import os
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DATASETS_DIR = BASE_DIR / "datasets"

RESEARCHER_PROFILES_PATH = DATASETS_DIR / "researcher_profiles.json"
PUBLICATIONS_PATH = DATASETS_DIR / "openalex_50000_clean.csv"
PATENTS_PATH = DATASETS_DIR / "2010_cleaned.csv"

OUTPUT_PATH = BASE_DIR / "researcher_intelligence.json"


# ============================================================
# 2. TEXT CLEANING UTILITIES
# ============================================================

def clean_text(value: Any) -> str:
    """
    Convert any value to a clean lowercase string.
    Handles NaN, None, empty strings, and non-string types.
    """
    if pd.isna(value) or value is None:
        return ""
    value = str(value).strip()
    if value.lower() in ("nan", "none", "null", ""):
        return ""
    return value.lower()


def normalize_field(value: Any) -> str:
    """
    Clean text and replace common separators (semicolons, pipes)
    with spaces so TF-IDF treats multi-value fields as natural language.
    """
    text = clean_text(value)
    if not text:
        return ""
    # Replace semicolons and pipes with spaces for TF-IDF
    text = re.sub(r"[;|]+", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def safe_str(value: Any) -> str:
    """Return a clean string or empty string — never NaN."""
    if pd.isna(value):
        return ""
    return str(value).strip()


# ============================================================
# 3. DATA LOADING & VALIDATION
# ============================================================

def load_researcher_profiles() -> list[dict]:
    """
    Load researcher_profiles.json — list of 8 researcher dicts.
    """
    with open(RESEARCHER_PROFILES_PATH, "r", encoding="utf-8") as f:
        profiles = json.load(f)
    print(f"  Loaded {len(profiles)} researcher profiles")
    return profiles


def load_publications() -> pd.DataFrame:
    """
    Load openalex_50000_clean.csv with ~50,000 publication records.
    Columns: id, title, publication_year, publication_date, type, authors,
             institutions, topics, primary_topic, concepts, cited_by_count,
             doi, source, is_retracted, open_access
    """
    df = pd.read_csv(PUBLICATIONS_PATH, low_memory=False)

    # Clean cited_by_count to numeric
    df["cited_by_count"] = pd.to_numeric(
        df["cited_by_count"], errors="coerce"
    ).fillna(0).astype(int)

    # Fill NaN in text fields
    for col in ["topics", "primary_topic", "concepts", "title"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    print(f"  Loaded {len(df):,} publication records")
    return df


def load_patents() -> pd.DataFrame:
    """
    Load 2010_cleaned.csv — Indian Patent Office 2010 filings.
    Key columns: application_number, title, field_of_invention,
                 classification_ipc, application_status, inventor_name,
                 applicant_name

    SCOPE NOTE: This dataset is 2010-only, India-only, and has no
    citation field. Patent strength scoring compensates using match
    count + status weighting instead of citation-based metrics.
    """
    df = pd.read_csv(PATENTS_PATH, low_memory=False)

    # Fill NaN in text fields used for matching
    for col in ["field_of_invention", "classification_ipc", "title",
                "application_status"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    print(f"  Loaded {len(df):,} patent records (2010, India-only)")
    return df


def validate_datasets(
    profiles: list[dict],
    pubs_df: pd.DataFrame,
    patents_df: pd.DataFrame,
) -> dict:
    """
    Run basic validation: row counts, missing-field report, dedupe check.
    Returns a summary dict for logging.
    """
    report = {
        "researcher_count": len(profiles),
        "publication_count": len(pubs_df),
        "patent_count": len(patents_df),
        "publication_duplicates": int(pubs_df.duplicated().sum()),
        "patent_duplicates": int(patents_df.duplicated().sum()),
        "publications_missing_topics": int(
            (pubs_df["topics"].apply(lambda x: clean_text(x) == "")).sum()
        ),
        "publications_missing_concepts": int(
            (pubs_df["concepts"].apply(lambda x: clean_text(x) == "")).sum()
        ),
        "patents_missing_field": int(
            (patents_df["field_of_invention"].apply(
                lambda x: clean_text(x) == ""
            )).sum()
        ),
    }

    print("\n  === Dataset Validation Report ===")
    for key, value in report.items():
        print(f"    {key}: {value}")

    return report


# ============================================================
# 4. RESEARCHER FEATURE EXTRACTION
# ============================================================

def build_researcher_text_profiles(
    profiles: list[dict],
) -> list[dict]:
    """
    For each researcher, build:
      - combined_text: research_domains + keywords + bio concatenated
      - expertise_keywords: flat list of normalized keywords

    Returns enriched list of researcher dicts.
    """
    enriched = []

    for researcher in profiles:
        # Combine research domains, keywords, and bio into one text blob
        domains_text = " ".join(researcher.get("research_domains", []))
        keywords_text = " ".join(researcher.get("keywords", []))
        bio_text = researcher.get("bio", "")

        combined_text = f"{domains_text} {keywords_text} {bio_text}"
        combined_text = normalize_field(combined_text)

        # Flat keyword list for explainability
        expertise_keywords = []
        for kw in researcher.get("keywords", []):
            kw_clean = clean_text(kw)
            if kw_clean:
                expertise_keywords.append(kw_clean)
        for dom in researcher.get("research_domains", []):
            dom_clean = clean_text(dom)
            if dom_clean and dom_clean not in expertise_keywords:
                expertise_keywords.append(dom_clean)

        enriched.append({
            **researcher,
            "_combined_text": combined_text,
            "_expertise_keywords": expertise_keywords,
        })

    print(f"  Built text profiles for {len(enriched)} researchers")
    return enriched


# ============================================================
# 5. PUBLICATION-STRENGTH SCORING ENGINE
# ============================================================

def build_publication_corpus(pubs_df: pd.DataFrame) -> list[str]:
    """
    Build a text corpus from each publication's topics + primary_topic
    + concepts, normalized into a single string per publication.
    """
    corpus = []
    for _, row in pubs_df.iterrows():
        parts = [
            normalize_field(row.get("topics", "")),
            normalize_field(row.get("primary_topic", "")),
            normalize_field(row.get("concepts", "")),
        ]
        text = " ".join(p for p in parts if p)
        corpus.append(text)
    return corpus


def score_publications_for_researchers(
    researchers: list[dict],
    pubs_df: pd.DataFrame,
    top_n: int = 50,
    similarity_threshold: float = 0.05,
) -> list[dict]:
    """
    For each researcher, compute TF-IDF cosine similarity against all
    publications. Select top-N matches above threshold.

    Publication strength score = f(match_count, avg_similarity, avg_citations)
    Normalized to 0-100.

    Returns researchers enriched with publication scores and match details.
    """
    print("\n  Building publication corpus...")

    pub_corpus = build_publication_corpus(pubs_df)

    # Combine researcher texts with publication corpus for joint TF-IDF
    researcher_texts = [r["_combined_text"] for r in researchers]
    full_corpus = researcher_texts + pub_corpus

    print("  Fitting TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=10000,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
    )
    tfidf_matrix = vectorizer.fit_transform(full_corpus)

    # Split back into researcher and publication matrices
    n_researchers = len(researchers)
    researcher_vectors = tfidf_matrix[:n_researchers]
    pub_vectors = tfidf_matrix[n_researchers:]

    # Compute cosine similarity: researchers × publications
    print("  Computing cosine similarity (researchers × publications)...")
    sim_matrix = cosine_similarity(researcher_vectors, pub_vectors)

    # Get feature names for explainability
    feature_names = vectorizer.get_feature_names_out()

    # Score each researcher
    pub_citations = pubs_df["cited_by_count"].values
    pub_titles = pubs_df["title"].values

    # Compute citation stats for normalization
    max_citation = pub_citations.max() if len(pub_citations) > 0 else 1
    avg_citation = pub_citations.mean() if len(pub_citations) > 0 else 0

    for i, researcher in enumerate(researchers):
        scores = sim_matrix[i]

        # Filter by threshold
        above_threshold = np.where(scores >= similarity_threshold)[0]

        if len(above_threshold) == 0:
            researcher["publication_strength_score"] = 0
            researcher["matched_publications_sample"] = []
            researcher["_pub_explanation_keywords"] = []
            continue

        # Sort by similarity descending, take top_n
        sorted_indices = above_threshold[
            np.argsort(scores[above_threshold])[::-1]
        ][:top_n]

        # Calculate score components
        match_count = len(sorted_indices)
        avg_similarity = float(scores[sorted_indices].mean())

        matched_citations = pub_citations[sorted_indices]
        avg_citations = float(matched_citations.mean())

        # Score formula: weighted combination
        # - match_count component (logarithmic to avoid domination)
        count_component = min(np.log1p(match_count) / np.log1p(50), 1.0)

        # - similarity component
        sim_component = avg_similarity

        # - citation component (normalized)
        cit_component = min(avg_citations / (max_citation + 1), 1.0)

        # Weighted combination: 30% count, 40% similarity, 30% citation
        raw_score = (
            0.30 * count_component
            + 0.40 * sim_component
            + 0.30 * cit_component
        )

        # Normalize to 0-100
        researcher["publication_strength_score"] = round(raw_score * 100, 2)

        # Top matched publications (for output)
        matched_pubs = []
        for idx in sorted_indices[:5]:
            matched_pubs.append({
                "title": safe_str(pub_titles[idx]),
                "similarity": round(float(scores[idx]), 4),
                "cited_by_count": int(pub_citations[idx]),
            })
        researcher["matched_publications_sample"] = matched_pubs

        # Extract which researcher keywords drove the matches
        # by looking at TF-IDF weights in the matching publications
        researcher["_pub_explanation_keywords"] = _extract_match_keywords(
            tfidf_matrix, i, sorted_indices[:10], feature_names
        )

    # Print summary
    scores_list = [
        r["publication_strength_score"] for r in researchers
    ]
    zero_matches = sum(1 for s in scores_list if s == 0)
    print(f"\n  Publication scoring complete:")
    print(f"    Researchers with 0 matches: {zero_matches}/{len(researchers)}")
    print(f"    Score range: {min(scores_list):.2f} — {max(scores_list):.2f}")
    print(f"    Mean score: {np.mean(scores_list):.2f}")

    return researchers


def _extract_match_keywords(
    tfidf_matrix,
    researcher_idx: int,
    matched_pub_indices: np.ndarray,
    feature_names: np.ndarray,
    top_k: int = 10,
) -> list[str]:
    """
    Extract the top TF-IDF features that appear in both the researcher
    profile AND the matched publications — these explain WHY a match
    was made.
    """
    # Researcher's TF-IDF vector
    researcher_vec = tfidf_matrix[researcher_idx].toarray().flatten()

    # Average TF-IDF across matched publications
    matched_vecs = tfidf_matrix[matched_pub_indices].toarray()
    avg_pub_vec = matched_vecs.mean(axis=0)

    # Element-wise product: features strong in both researcher and pubs
    overlap = researcher_vec * avg_pub_vec

    # Top-k feature indices
    top_indices = np.argsort(overlap)[::-1][:top_k]

    keywords = []
    for idx in top_indices:
        if overlap[idx] > 0:
            keywords.append(feature_names[idx])

    return keywords


# ============================================================
# 6. PATENT-STRENGTH SCORING ENGINE
# ============================================================

# Patent status weights — compensate for missing citation data.
# Granted/published patents indicate higher research impact.
PATENT_STATUS_WEIGHTS = {
    "granted": 1.0,
    "sealed": 1.0,
    "published": 0.85,
    "filed": 0.5,
    "pending": 0.5,
    "deemed to be withdrawn": 0.1,
    "withdrawn": 0.1,
    "refused": 0.1,
    "rejected": 0.1,
    "abandoned": 0.1,
    "rejected u/s 15": 0.1,
    "rejected u/s 14": 0.1,
}


def _get_patent_status_weight(status: str) -> float:
    """
    Map a patent application_status to a weight between 0 and 1.
    Uses fuzzy matching — checks if the status string contains
    any known keyword.
    """
    status_lower = safe_str(status).lower()
    if not status_lower:
        return 0.3  # default for unknown status

    for keyword, weight in PATENT_STATUS_WEIGHTS.items():
        if keyword in status_lower:
            return weight

    return 0.3  # default for unrecognized status


def build_patent_corpus(patents_df: pd.DataFrame) -> list[str]:
    """
    Build a text corpus from each patent's field_of_invention
    + classification_ipc, normalized into a single string.
    """
    corpus = []
    for _, row in patents_df.iterrows():
        parts = [
            normalize_field(row.get("field_of_invention", "")),
            normalize_field(row.get("classification_ipc", "")),
        ]
        text = " ".join(p for p in parts if p)
        corpus.append(text)
    return corpus


def score_patents_for_researchers(
    researchers: list[dict],
    patents_df: pd.DataFrame,
    top_n: int = 50,
    similarity_threshold: float = 0.02,
) -> list[dict]:
    """
    For each researcher, compute TF-IDF cosine similarity against all
    patents. Select top-N matches above threshold.

    Patent strength score = f(match_count, avg_similarity, status_weight)
    Normalized to 0-100.

    SCOPE NOTE: Patent dataset is 2010-only, India-only, with no
    citation field. Scores compensate using status weighting:
    granted/published > pending > withdrawn/refused.

    Returns researchers enriched with patent scores and match details.
    """
    print("\n  Building patent corpus...")

    patent_corpus = build_patent_corpus(patents_df)

    # Filter out empty corpus entries (patents with no field/ipc)
    valid_mask = [bool(c.strip()) for c in patent_corpus]

    if not any(valid_mask):
        print("  WARNING: No valid patent text found for matching.")
        for r in researchers:
            r["patent_strength_score"] = 0
            r["matched_patents_sample"] = []
            r["_patent_explanation_keywords"] = []
        return researchers

    # Combine researcher texts with patent corpus for joint TF-IDF
    researcher_texts = [r["_combined_text"] for r in researchers]
    full_corpus = researcher_texts + patent_corpus

    print("  Fitting TF-IDF vectorizer for patents...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
    )
    tfidf_matrix = vectorizer.fit_transform(full_corpus)

    n_researchers = len(researchers)
    researcher_vectors = tfidf_matrix[:n_researchers]
    patent_vectors = tfidf_matrix[n_researchers:]

    # Compute cosine similarity
    print("  Computing cosine similarity (researchers × patents)...")
    sim_matrix = cosine_similarity(researcher_vectors, patent_vectors)

    feature_names = vectorizer.get_feature_names_out()

    # Patent metadata for scoring
    patent_statuses = patents_df["application_status"].values
    patent_titles = patents_df["title"].values

    # Compute status weights for all patents
    status_weights = np.array([
        _get_patent_status_weight(s) for s in patent_statuses
    ])

    for i, researcher in enumerate(researchers):
        scores = sim_matrix[i]

        # Filter by threshold
        above_threshold = np.where(scores >= similarity_threshold)[0]

        if len(above_threshold) == 0:
            researcher["patent_strength_score"] = 0
            researcher["matched_patents_sample"] = []
            researcher["_patent_explanation_keywords"] = []
            continue

        # Sort by similarity, take top_n
        sorted_indices = above_threshold[
            np.argsort(scores[above_threshold])[::-1]
        ][:top_n]

        match_count = len(sorted_indices)
        avg_similarity = float(scores[sorted_indices].mean())

        # Weighted status score (mean status weight of matched patents)
        matched_status_weights = status_weights[sorted_indices]
        avg_status_weight = float(matched_status_weights.mean())

        # Score formula
        count_component = min(np.log1p(match_count) / np.log1p(20), 1.0)
        sim_component = avg_similarity
        status_component = avg_status_weight

        # Weighted: 25% count, 35% similarity, 40% status
        raw_score = (
            0.25 * count_component
            + 0.35 * sim_component
            + 0.40 * status_component
        )

        researcher["patent_strength_score"] = round(raw_score * 100, 2)

        # Top matched patents
        matched_pats = []
        for idx in sorted_indices[:5]:
            matched_pats.append({
                "title": safe_str(patent_titles[idx]),
                "similarity": round(float(scores[idx]), 4),
                "status": safe_str(patent_statuses[idx]),
                "status_weight": round(float(status_weights[idx]), 2),
            })
        researcher["matched_patents_sample"] = matched_pats

        # Explanation keywords
        researcher["_patent_explanation_keywords"] = (
            _extract_match_keywords(
                tfidf_matrix, i, sorted_indices[:10], feature_names
            )
        )

    # Print summary
    scores_list = [
        r["patent_strength_score"] for r in researchers
    ]
    zero_matches = sum(1 for s in scores_list if s == 0)
    print(f"\n  Patent scoring complete:")
    print(f"    Researchers with 0 patent matches: "
          f"{zero_matches}/{len(researchers)}")
    print(f"    Score range: {min(scores_list):.2f} — {max(scores_list):.2f}")
    print(f"    Mean score: {np.mean(scores_list):.2f}")

    return researchers


# ============================================================
# 7. COMBINED RESEARCHER INTELLIGENCE SCORE
# ============================================================

def compute_combined_scores(
    researchers: list[dict],
    pub_weight: float = 0.60,
    patent_weight: float = 0.40,
) -> list[dict]:
    """
    Combine publication and patent scores into an overall researcher
    intelligence score. Default weights: 60% publication, 40% patent.

    Also derives top_expertise_areas from the strongest keyword overlaps
    across both publication and patent matches.
    """
    for researcher in researchers:
        pub_score = researcher.get("publication_strength_score", 0)
        patent_score = researcher.get("patent_strength_score", 0)

        # Weighted combination
        overall = pub_weight * pub_score + patent_weight * patent_score
        researcher["overall_researcher_score"] = round(overall, 2)

        # Derive top expertise areas from explanation keywords
        pub_kw = researcher.get("_pub_explanation_keywords", [])
        patent_kw = researcher.get("_patent_explanation_keywords", [])
        researcher_keywords = researcher.get("_expertise_keywords", [])

        # Combine and rank: researcher's own keywords first,
        # then keywords that drove publication matches,
        # then keywords that drove patent matches
        expertise_map: dict[str, float] = {}

        for kw in researcher_keywords:
            expertise_map[kw] = expertise_map.get(kw, 0) + 3.0

        for kw in pub_kw:
            expertise_map[kw] = expertise_map.get(kw, 0) + 2.0

        for kw in patent_kw:
            expertise_map[kw] = expertise_map.get(kw, 0) + 1.0

        # Sort by combined weight, take top 8
        sorted_expertise = sorted(
            expertise_map.items(), key=lambda x: x[1], reverse=True
        )[:8]

        researcher["top_expertise_areas"] = [
            kw for kw, _ in sorted_expertise
        ]

    return researchers


# ============================================================
# 8. EXPLAINABILITY LAYER
# ============================================================

def generate_explanations(researchers: list[dict]) -> list[dict]:
    """
    For each researcher, produce a short human-readable explanation
    string describing which keywords/topics drove the intelligence score.
    """
    for researcher in researchers:
        pub_score = researcher.get("publication_strength_score", 0)
        patent_score = researcher.get("patent_strength_score", 0)
        overall = researcher.get("overall_researcher_score", 0)

        expertise = researcher.get("top_expertise_areas", [])
        pub_matches = researcher.get("matched_publications_sample", [])
        patent_matches = researcher.get("matched_patents_sample", [])

        parts = []

        # Overall assessment
        if overall >= 60:
            strength = "strong"
        elif overall >= 30:
            strength = "moderate"
        elif overall > 0:
            strength = "emerging"
        else:
            strength = "limited"

        expertise_str = ", ".join(expertise[:5]) if expertise else "N/A"
        parts.append(
            f"{researcher['name']} demonstrates {strength} research "
            f"intelligence (score: {overall:.1f}/100)."
        )

        parts.append(
            f"Top expertise areas: {expertise_str}."
        )

        if pub_score > 0:
            parts.append(
                f"Publication strength: {pub_score:.1f}/100 based on "
                f"{len(pub_matches)} top-matched publications."
            )
        else:
            parts.append(
                "No significant publication matches found with current "
                "similarity threshold."
            )

        if patent_score > 0:
            parts.append(
                f"Patent strength: {patent_score:.1f}/100 based on "
                f"{len(patent_matches)} top-matched patents "
                f"(2010 Indian Patent Office data, status-weighted)."
            )
        else:
            parts.append(
                "No significant patent matches found. Note: patent dataset "
                "is limited to 2010 Indian filings."
            )

        # Key driving keywords
        pub_kw = researcher.get("_pub_explanation_keywords", [])
        patent_kw = researcher.get("_patent_explanation_keywords", [])
        if pub_kw or patent_kw:
            all_kw = list(dict.fromkeys(pub_kw[:5] + patent_kw[:5]))
            parts.append(
                f"Key matching keywords: {', '.join(all_kw)}."
            )

        researcher["explanation"] = " ".join(parts)

    return researchers


# ============================================================
# 9. OUTPUT FORMATTING
# ============================================================

def format_output(researchers: list[dict]) -> list[dict]:
    """
    Clean up researcher dicts to match the required output schema:
    {
        "researcher_id": "...",
        "name": "...",
        "institution": "...",
        "top_expertise_areas": [...],
        "publication_strength_score": 0-100,
        "patent_strength_score": 0-100,
        "overall_researcher_score": 0-100,
        "matched_publications_sample": [...],
        "matched_patents_sample": [...],
        "explanation": "..."
    }
    """
    output = []
    for r in researchers:
        output.append({
            "researcher_id": r.get("id", ""),
            "name": r.get("name", ""),
            "institution": r.get("institution", ""),
            "top_expertise_areas": r.get("top_expertise_areas", []),
            "publication_strength_score": r.get(
                "publication_strength_score", 0
            ),
            "patent_strength_score": r.get("patent_strength_score", 0),
            "overall_researcher_score": r.get("overall_researcher_score", 0),
            "matched_publications_sample": r.get(
                "matched_publications_sample", []
            ),
            "matched_patents_sample": r.get("matched_patents_sample", []),
            "explanation": r.get("explanation", ""),
        })

    # Sort by overall_researcher_score descending
    output.sort(key=lambda x: x["overall_researcher_score"], reverse=True)
    return output


# ============================================================
# 10. SANITY CHECK & VALIDATION
# ============================================================

def print_validation_summary(output: list[dict]) -> None:
    """
    Print a sanity-check summary for the final output:
    - How many researchers got 0 scores
    - Score distribution
    - One fully worked example
    """
    print("\n" + "=" * 70)
    print("SANITY CHECK — RESEARCHER INTELLIGENCE SUMMARY")
    print("=" * 70)

    zero_pub = sum(
        1 for r in output if r["publication_strength_score"] == 0
    )
    zero_patent = sum(
        1 for r in output if r["patent_strength_score"] == 0
    )
    zero_overall = sum(
        1 for r in output if r["overall_researcher_score"] == 0
    )

    print(f"\n  Total researchers: {len(output)}")
    print(f"  Researchers with 0 publication score: {zero_pub}")
    print(f"  Researchers with 0 patent score: {zero_patent}")
    print(f"  Researchers with 0 overall score: {zero_overall}")

    if zero_overall == len(output):
        print("\n  ⚠ WARNING: All researchers have 0 overall score!")
        print("    This may indicate the similarity threshold is too strict.")
        print("    Consider lowering the threshold or expanding keyword sets.")

    # Score distribution
    overall_scores = [r["overall_researcher_score"] for r in output]
    print(f"\n  Overall score distribution:")
    print(f"    Min:    {min(overall_scores):.2f}")
    print(f"    Max:    {max(overall_scores):.2f}")
    print(f"    Mean:   {np.mean(overall_scores):.2f}")
    print(f"    Median: {np.median(overall_scores):.2f}")
    print(f"    Std:    {np.std(overall_scores):.2f}")

    # Fully worked example
    print("\n  --- Fully Worked Example ---")
    example = output[0]  # Top-scoring researcher
    print(f"  Researcher: {example['name']}")
    print(f"  Institution: {example['institution']}")
    print(f"  Top Expertise: {', '.join(example['top_expertise_areas'][:5])}")
    print(f"  Publication Strength: "
          f"{example['publication_strength_score']:.2f}/100")
    print(f"  Patent Strength: "
          f"{example['patent_strength_score']:.2f}/100")
    print(f"  Overall Score: "
          f"{example['overall_researcher_score']:.2f}/100")
    print(f"  Matched Publications (top 3):")
    for j, pub in enumerate(example["matched_publications_sample"][:3], 1):
        print(f"    {j}. {pub['title'][:80]}...")
        print(f"       Similarity: {pub['similarity']:.4f}, "
              f"Citations: {pub['cited_by_count']}")
    print(f"  Matched Patents (top 3):")
    for j, pat in enumerate(example["matched_patents_sample"][:3], 1):
        print(f"    {j}. {pat['title'][:80]}...")
        print(f"       Similarity: {pat['similarity']:.4f}, "
              f"Status: {pat['status']}")
    print(f"  Explanation: {example['explanation'][:200]}...")

    # Full ranking
    print("\n  --- Researcher Rankings ---")
    for rank, r in enumerate(output, 1):
        print(f"  #{rank} {r['name']} ({r['institution']})")
        print(f"     Pub: {r['publication_strength_score']:.1f} | "
              f"Patent: {r['patent_strength_score']:.1f} | "
              f"Overall: {r['overall_researcher_score']:.1f}")


# ============================================================
# 11. MAIN PIPELINE
# ============================================================

def run_intelligence_pipeline() -> list[dict]:
    """
    Execute the full Researcher Intelligence pipeline:
    1. Load and validate all datasets
    2. Extract researcher features
    3. Score publications
    4. Score patents
    5. Compute combined scores
    6. Generate explanations
    7. Format output
    8. Save to JSON
    9. Print validation summary
    """
    print("\n" + "=" * 70)
    print("RESEARCHER INTELLIGENCE ENGINE — MILESTONE 3")
    print("=" * 70)

    # Step 1: Load datasets
    print("\n[1/8] Loading datasets...")
    profiles = load_researcher_profiles()
    pubs_df = load_publications()
    patents_df = load_patents()

    # Step 2: Validate
    print("\n[2/8] Validating datasets...")
    validation_report = validate_datasets(profiles, pubs_df, patents_df)

    # Step 3: Build researcher text profiles
    print("\n[3/8] Building researcher text profiles...")
    researchers = build_researcher_text_profiles(profiles)

    # Step 4: Score publications
    print("\n[4/8] Scoring publications...")
    researchers = score_publications_for_researchers(
        researchers, pubs_df
    )

    # Step 5: Score patents
    print("\n[5/8] Scoring patents...")
    researchers = score_patents_for_researchers(
        researchers, patents_df
    )

    # Step 6: Compute combined scores
    print("\n[6/8] Computing combined intelligence scores...")
    researchers = compute_combined_scores(researchers)

    # Step 7: Generate explanations
    print("\n[7/8] Generating explanations...")
    researchers = generate_explanations(researchers)

    # Step 8: Format and save
    print("\n[8/8] Formatting output and saving...")
    output = format_output(researchers)

    # Save to JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"  Saved to: {OUTPUT_PATH}")

    # Validation summary
    print_validation_summary(output)

    print("\n" + "=" * 70)
    print("RESEARCHER INTELLIGENCE PIPELINE COMPLETE")
    print("=" * 70)

    return output


# ============================================================
# 12. FASTAPI-READY DATA ACCESS
# ============================================================

# Global cache — populated on first request or explicit init
_intelligence_cache: list[dict] | None = None


def get_intelligence_data() -> list[dict]:
    """
    Return cached intelligence data. Runs pipeline if not yet loaded.
    Used by FastAPI endpoints.
    """
    global _intelligence_cache
    if _intelligence_cache is None:
        _intelligence_cache = run_intelligence_pipeline()
    return _intelligence_cache


def get_researcher_by_id(researcher_id: str) -> dict | None:
    """
    Look up a single researcher by their ID.
    Returns None if not found (for 404 handling).
    """
    data = get_intelligence_data()
    for r in data:
        if r["researcher_id"] == researcher_id:
            return r
    return None


def get_all_researchers_sorted() -> list[dict]:
    """
    Return all researchers sorted by overall_researcher_score descending.
    """
    data = get_intelligence_data()
    return sorted(
        data, key=lambda x: x["overall_researcher_score"], reverse=True
    )


# ============================================================
# 13. STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":
    run_intelligence_pipeline()
