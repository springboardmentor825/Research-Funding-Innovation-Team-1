"""
=============================================================
OPENALEX 50,000 - EDA AND TREND ANALYSIS
=============================================================

Input:
    data/processed/openalex_50000_clean.csv

Output:
    analysis/results/

This script performs:
    1. Publication year analysis
    2. Domain analysis
    3. Topic analysis
    4. Author analysis
    5. Institution analysis
    6. Source/journal analysis
    7. Citation analysis
    8. Open-access analysis
    9. Retraction analysis
   10. Top-cited paper analysis

Dataset:
    50,000 OpenAlex publications
    Years: 2015-2025
    Columns: 15

=============================================================
"""

import os
import re
import ast
import pandas as pd
import numpy as np


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "openalex_50000_clean.csv"
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "analysis",
    "results"
)

os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def save_csv(df, filename):
    """
    Save DataFrame to the results directory.
    """
    path = os.path.join(RESULTS_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved: {path}")
    return path


def clean_text(value):
    """
    Convert a value to a clean string.
    """
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.lower() in ["nan", "none", "null", ""]:
        return ""

    return value


def split_items(value):
    """
    Split semicolon-separated fields.

    Example:
        'A; B; C'

    becomes:
        ['A', 'B', 'C']
    """

    value = clean_text(value)

    if not value:
        return []

    # Normal semicolon-separated OpenAlex fields
    items = value.split(";")

    cleaned = []

    for item in items:
        item = item.strip()

        if item:
            cleaned.append(item)

    return cleaned


def normalize_bool(value):
    """
    Convert boolean-like values to True/False.
    """

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    if value in ["true", "1", "yes"]:
        return True

    return False


# ============================================================
# 3. LOAD DATASET
# ============================================================

print("\n" + "=" * 70)
print("OPENALEX 50,000 - EDA AND TREND ANALYSIS")
print("=" * 70)

print("\nLoading dataset...")

if not os.path.exists(INPUT_FILE):
    print("\nERROR: Dataset file not found!")
    print(f"Expected file:")
    print(INPUT_FILE)
    print("\nPlease check that your cleaned dataset exists.")
    raise FileNotFoundError(INPUT_FILE)

df = pd.read_csv(INPUT_FILE, low_memory=False)

print("\nDataset loaded successfully.")

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")

print("\nColumns:")

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")


# ============================================================
# 4. BASIC DATA INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("BASIC DATA INFORMATION")
print("=" * 70)

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

if "id" in df.columns:
    print("\nDuplicate OpenAlex IDs:")
    print(df["id"].duplicated().sum())


# ============================================================
# 5. PREPARE IMPORTANT COLUMNS
# ============================================================

if "publication_year" in df.columns:
    df["publication_year"] = pd.to_numeric(
        df["publication_year"],
        errors="coerce"
    )

if "cited_by_count" in df.columns:
    df["cited_by_count"] = pd.to_numeric(
        df["cited_by_count"],
        errors="coerce"
    ).fillna(0)

if "is_retracted" in df.columns:
    df["is_retracted"] = df["is_retracted"].apply(normalize_bool)

if "open_access" in df.columns:
    df["open_access"] = df["open_access"].apply(normalize_bool)


# ============================================================
# 6. PUBLICATION YEAR TREND
# ============================================================

print("\n" + "=" * 70)
print("1. PUBLICATION YEAR TREND")
print("=" * 70)

year_trend = (
    df.groupby("publication_year")
      .size()
      .reset_index(name="publication_count")
      .sort_values("publication_year")
)

# Calculate percentage growth
year_trend["growth_percentage"] = (
    year_trend["publication_count"]
    .pct_change()
    .mul(100)
    .round(2)
)

# First year has no previous year
year_trend["growth_percentage"] = (
    year_trend["growth_percentage"]
    .replace([np.inf, -np.inf], np.nan)
)

print("\nPublication count by year:")
print(year_trend.to_string(index=False))

save_csv(
    year_trend,
    "publication_year_trend.csv"
)


# ============================================================
# 7. DOMAIN ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("2. DOMAIN ANALYSIS")
print("=" * 70)

domain_records = []

for _, row in df.iterrows():

    year = row["publication_year"]

    topics = split_items(row.get("topics", ""))

    # Extract domains from topics.
    # OpenAlex topics in this dataset are represented by
    # topic names. We classify them using keyword-based
    # domain rules.

    text = " ".join(topics).lower()

    if any(
        word in text
        for word in [
            "health",
            "medical",
            "medicine",
            "clinical",
            "disease",
            "public health",
            "healthcare"
        ]
    ):
        domain = "Health Sciences"

    elif any(
        word in text
        for word in [
            "biology",
            "ecology",
            "genetics",
            "biochemistry",
            "microbiology",
            "plant",
            "animal",
            "environment"
        ]
    ):
        domain = "Life Sciences"

    elif any(
        word in text
        for word in [
            "physics",
            "chemistry",
            "engineering",
            "materials",
            "energy",
            "mathematics",
            "computer",
            "artificial intelligence",
            "machine learning",
            "technology"
        ]
    ):
        domain = "Physical Sciences"

    else:
        domain = "Social Sciences"

    domain_records.append(
        {
            "publication_year": year,
            "domain": domain
        }
    )


domain_df = pd.DataFrame(domain_records)


# Overall domain distribution

domain_distribution = (
    domain_df.groupby("domain")
             .size()
             .reset_index(name="publication_count")
             .sort_values(
                 "publication_count",
                 ascending=False
             )
)

domain_distribution["percentage"] = (
    domain_distribution["publication_count"]
    / len(df)
    * 100
).round(2)

print("\nDomain distribution:")
print(domain_distribution.to_string(index=False))

save_csv(
    domain_distribution,
    "domain_distribution.csv"
)


# ============================================================
# 8. DOMAIN YEAR TREND
# ============================================================

domain_year_trend = (
    domain_df.groupby(
        ["publication_year", "domain"]
    )
    .size()
    .reset_index(name="publication_count")
    .sort_values(
        ["publication_year", "publication_count"],
        ascending=[True, False]
    )
)

print("\nDomain trend by year:")
print(domain_year_trend.to_string(index=False))

save_csv(
    domain_year_trend,
    "domain_year_trend.csv"
)


# ============================================================
# 9. TOP RESEARCH TOPICS
# ============================================================

print("\n" + "=" * 70)
print("3. TOP RESEARCH TOPICS")
print("=" * 70)

topic_records = []

for value in df["topics"]:

    topics = split_items(value)

    for topic in topics:

        topic_records.append(
            {
                "topic": topic
            }
        )


topics_df = pd.DataFrame(topic_records)

if not topics_df.empty:

    topic_distribution = (
        topics_df.groupby("topic")
        .size()
        .reset_index(name="publication_count")
        .sort_values(
            "publication_count",
            ascending=False
        )
    )

    topic_distribution["percentage"] = (
        topic_distribution["publication_count"]
        / len(df)
        * 100
    ).round(2)

else:

    topic_distribution = pd.DataFrame(
        columns=[
            "topic",
            "publication_count",
            "percentage"
        ]
    )


print("\nTop 20 research topics:")

print(
    topic_distribution.head(20)
    .to_string(index=False)
)

save_csv(
    topic_distribution,
    "topic_distribution.csv"
)


# ============================================================
# 10. TOPIC YEAR TREND
# ============================================================

topic_year_records = []

for _, row in df.iterrows():

    year = row["publication_year"]

    topics = split_items(row["topics"])

    for topic in topics:

        topic_year_records.append(
            {
                "publication_year": year,
                "topic": topic
            }
        )


topic_year_df = pd.DataFrame(topic_year_records)

if not topic_year_df.empty:

    topic_year_trend = (
        topic_year_df
        .groupby(
            ["publication_year", "topic"]
        )
        .size()
        .reset_index(
            name="publication_count"
        )
        .sort_values(
            [
                "publication_year",
                "publication_count"
            ],
            ascending=[True, False]
        )
    )

else:

    topic_year_trend = pd.DataFrame(
        columns=[
            "publication_year",
            "topic",
            "publication_count"
        ]
    )


save_csv(
    topic_year_trend,
    "topic_year_trend.csv"
)


# ============================================================
# 11. PRIMARY TOPIC ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("4. PRIMARY TOPIC ANALYSIS")
print("=" * 70)

primary_topic_distribution = (
    df["primary_topic"]
    .fillna("Unknown")
    .replace("", "Unknown")
    .value_counts()
    .reset_index()
)

primary_topic_distribution.columns = [
    "primary_topic",
    "publication_count"
]

primary_topic_distribution["percentage"] = (
    primary_topic_distribution["publication_count"]
    / len(df)
    * 100
).round(2)

print("\nTop 20 primary topics:")

print(
    primary_topic_distribution.head(20)
    .to_string(index=False)
)

save_csv(
    primary_topic_distribution,
    "primary_topic_distribution.csv"
)


# ============================================================
# 12. AUTHOR PRODUCTIVITY
# ============================================================

print("\n" + "=" * 70)
print("5. AUTHOR PRODUCTIVITY")
print("=" * 70)

author_records = []

for value in df["authors"]:

    authors = split_items(value)

    for author in authors:

        author_records.append(
            {
                "author": author
            }
        )


authors_df = pd.DataFrame(author_records)

if not authors_df.empty:

    author_productivity = (
        authors_df.groupby("author")
        .size()
        .reset_index(name="publication_count")
        .sort_values(
            "publication_count",
            ascending=False
        )
    )

else:

    author_productivity = pd.DataFrame(
        columns=[
            "author",
            "publication_count"
        ]
    )


print("\nTop 20 authors:")

print(
    author_productivity.head(20)
    .to_string(index=False)
)

save_csv(
    author_productivity,
    "author_productivity.csv"
)


# ============================================================
# 13. INSTITUTION PRODUCTIVITY
# ============================================================

print("\n" + "=" * 70)
print("6. INSTITUTION PRODUCTIVITY")
print("=" * 70)

institution_records = []

for value in df["institutions"]:

    institutions = split_items(value)

    for institution in institutions:

        institution_records.append(
            {
                "institution": institution
            }
        )


institutions_df = pd.DataFrame(
    institution_records
)

if not institutions_df.empty:

    institution_productivity = (
        institutions_df
        .groupby("institution")
        .size()
        .reset_index(
            name="publication_count"
        )
        .sort_values(
            "publication_count",
            ascending=False
        )
    )

else:

    institution_productivity = pd.DataFrame(
        columns=[
            "institution",
            "publication_count"
        ]
    )


print("\nTop 20 institutions:")

print(
    institution_productivity.head(20)
    .to_string(index=False)
)

save_csv(
    institution_productivity,
    "institution_productivity.csv"
)


# ============================================================
# 14. SOURCE / JOURNAL ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("7. SOURCE / JOURNAL ANALYSIS")
print("=" * 70)

source_distribution = (
    df["source"]
    .fillna("Unknown")
    .replace("", "Unknown")
    .value_counts()
    .reset_index()
)

source_distribution.columns = [
    "source",
    "publication_count"
]

source_distribution["percentage"] = (
    source_distribution["publication_count"]
    / len(df)
    * 100
).round(2)

print("\nTop 20 sources:")

print(
    source_distribution.head(20)
    .to_string(index=False)
)

save_csv(
    source_distribution,
    "source_distribution.csv"
)


# ============================================================
# 15. CITATION TREND
# ============================================================

print("\n" + "=" * 70)
print("8. CITATION ANALYSIS")
print("=" * 70)

citation_trend = (
    df.groupby("publication_year")
    .agg(
        publication_count=(
            "id",
            "count"
        ),
        total_citations=(
            "cited_by_count",
            "sum"
        ),
        average_citations=(
            "cited_by_count",
            "mean"
        ),
        median_citations=(
            "cited_by_count",
            "median"
        ),
        maximum_citations=(
            "cited_by_count",
            "max"
        )
    )
    .reset_index()
)

citation_trend["average_citations"] = (
    citation_trend["average_citations"]
    .round(2)
)

print("\nCitation trend:")
print(
    citation_trend.to_string(index=False)
)

save_csv(
    citation_trend,
    "citation_trend.csv"
)


# ============================================================
# 16. TOP CITED PAPERS
# ============================================================

print("\n" + "=" * 70)
print("9. TOP CITED PAPERS")
print("=" * 70)

top_cited_columns = [
    "id",
    "title",
    "publication_year",
    "authors",
    "source",
    "cited_by_count",
    "doi"
]

available_columns = [
    column
    for column in top_cited_columns
    if column in df.columns
]

top_cited_papers = (
    df[available_columns]
    .sort_values(
        "cited_by_count",
        ascending=False
    )
    .head(100)
    .reset_index(drop=True)
)

print("\nTop 20 most cited papers:")

print(
    top_cited_papers.head(20)
    .to_string(index=False)
)

save_csv(
    top_cited_papers,
    "top_cited_papers.csv"
)


# ============================================================
# 17. OPEN ACCESS ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("10. OPEN ACCESS ANALYSIS")
print("=" * 70)

open_access_distribution = (
    df["open_access"]
    .value_counts()
    .reset_index()
)

open_access_distribution.columns = [
    "open_access",
    "publication_count"
]

open_access_distribution["percentage"] = (
    open_access_distribution["publication_count"]
    / len(df)
    * 100
).round(2)

print("\nOpen-access distribution:")

print(
    open_access_distribution
    .to_string(index=False)
)

save_csv(
    open_access_distribution,
    "open_access_distribution.csv"
)


# ============================================================
# 18. OPEN ACCESS YEAR TREND
# ============================================================

open_access_year_trend = (
    df.groupby(
        [
            "publication_year",
            "open_access"
        ]
    )
    .size()
    .reset_index(
        name="publication_count"
    )
    .sort_values(
        [
            "publication_year",
            "open_access"
        ]
    )
)

save_csv(
    open_access_year_trend,
    "open_access_year_trend.csv"
)


# ============================================================
# 19. RETRACTION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("11. RETRACTION ANALYSIS")
print("=" * 70)

retraction_distribution = (
    df["is_retracted"]
    .value_counts()
    .reset_index()
)

retraction_distribution.columns = [
    "is_retracted",
    "publication_count"
]

retraction_distribution["percentage"] = (
    retraction_distribution["publication_count"]
    / len(df)
    * 100
).round(4)

print("\nRetraction distribution:")

print(
    retraction_distribution
    .to_string(index=False)
)

save_csv(
    retraction_distribution,
    "retraction_distribution.csv"
)


# ============================================================
# 20. RETRACTION YEAR TREND
# ============================================================

retraction_year_trend = (
    df.groupby(
        [
            "publication_year",
            "is_retracted"
        ]
    )
    .size()
    .reset_index(
        name="publication_count"
    )
    .sort_values(
        [
            "publication_year",
            "is_retracted"
        ]
    )
)

save_csv(
    retraction_year_trend,
    "retraction_year_trend.csv"
)


# ============================================================
# 21. TYPE DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("12. PUBLICATION TYPE ANALYSIS")
print("=" * 70)

type_distribution = (
    df["type"]
    .fillna("Unknown")
    .replace("", "Unknown")
    .value_counts()
    .reset_index()
)

type_distribution.columns = [
    "publication_type",
    "publication_count"
]

type_distribution["percentage"] = (
    type_distribution["publication_count"]
    / len(df)
    * 100
).round(2)

print("\nPublication types:")

print(
    type_distribution.to_string(index=False)
)

save_csv(
    type_distribution,
    "publication_type_distribution.csv"
)


# ============================================================
# 22. DOI AVAILABILITY
# ============================================================

print("\n" + "=" * 70)
print("13. DOI ANALYSIS")
print("=" * 70)

doi_available = (
    df["doi"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
)

doi_distribution = pd.DataFrame(
    {
        "doi_available": [
            True,
            False
        ],
        "publication_count": [
            int(doi_available.sum()),
            int((~doi_available).sum())
        ]
    }
)

doi_distribution["percentage"] = (
    doi_distribution["publication_count"]
    / len(df)
    * 100
).round(2)

print("\nDOI availability:")

print(
    doi_distribution.to_string(index=False)
)

save_csv(
    doi_distribution,
    "doi_distribution.csv"
)


# ============================================================
# 23. PUBLICATION TYPE BY YEAR
# ============================================================

type_year_trend = (
    df.groupby(
        [
            "publication_year",
            "type"
        ]
    )
    .size()
    .reset_index(
        name="publication_count"
    )
    .sort_values(
        [
            "publication_year",
            "publication_count"
        ],
        ascending=[
            True,
            False
        ]
    )
)

save_csv(
    type_year_trend,
    "publication_type_year_trend.csv"
)


# ============================================================
# 24. YEARLY SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("14. YEARLY SUMMARY")
print("=" * 70)

yearly_summary = (
    df.groupby("publication_year")
    .agg(
        publication_count=(
            "id",
            "count"
        ),
        total_citations=(
            "cited_by_count",
            "sum"
        ),
        average_citations=(
            "cited_by_count",
            "mean"
        ),
        median_citations=(
            "cited_by_count",
            "median"
        ),
        open_access_count=(
            "open_access",
            "sum"
        ),
        retracted_count=(
            "is_retracted",
            "sum"
        )
    )
    .reset_index()
)

yearly_summary["average_citations"] = (
    yearly_summary["average_citations"]
    .round(2)
)

yearly_summary["open_access_percentage"] = (
    yearly_summary["open_access_count"]
    / yearly_summary["publication_count"]
    * 100
).round(2)

yearly_summary["retracted_percentage"] = (
    yearly_summary["retracted_count"]
    / yearly_summary["publication_count"]
    * 100
).round(4)

print(
    yearly_summary.to_string(index=False)
)

save_csv(
    yearly_summary,
    "yearly_summary.csv"
)


# ============================================================
# 25. DATASET SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("15. DATASET SUMMARY")
print("=" * 70)

summary = pd.DataFrame(
    {
        "metric": [
            "Total publications",
            "Total columns",
            "Minimum publication year",
            "Maximum publication year",
            "Total citations",
            "Average citations",
            "Median citations",
            "Maximum citations",
            "Open access publications",
            "Retracted publications",
            "Publications with DOI",
            "Unique OpenAlex IDs"
        ],
        "value": [
            len(df),
            len(df.columns),
            int(df["publication_year"].min()),
            int(df["publication_year"].max()),
            int(df["cited_by_count"].sum()),
            round(
                df["cited_by_count"].mean(),
                2
            ),
            round(
                df["cited_by_count"].median(),
                2
            ),
            int(
                df["cited_by_count"].max()
            ),
            int(
                df["open_access"].sum()
            ),
            int(
                df["is_retracted"].sum()
            ),
            int(
                doi_available.sum()
            ),
            int(
                df["id"].nunique()
            )
        ]
    }
)

print(
    summary.to_string(index=False)
)

save_csv(
    summary,
    "dataset_summary.csv"
)


# ============================================================
# 26. FINAL VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("FINAL VALIDATION")
print("=" * 70)

print(
    f"\nTotal rows: {len(df):,}"
)

print(
    f"Total columns: {len(df.columns)}"
)

print(
    f"Unique OpenAlex IDs: {df['id'].nunique():,}"
)

print(
    f"Duplicate rows: {df.duplicated().sum()}"
)

print(
    f"Missing values: {int(df.isnull().sum().sum())}"
)

print(
    f"Year range: "
    f"{int(df['publication_year'].min())} - "
    f"{int(df['publication_year'].max())}"
)


# ============================================================
# 27. FINISH
# ============================================================

print("\n" + "=" * 70)
print("EDA AND TREND ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nResults saved in:")

print(RESULTS_DIR)

print("\nGenerated analysis files:")

for filename in sorted(os.listdir(RESULTS_DIR)):

    if filename.endswith(".csv"):
        print(f"  ✓ {filename}")

print("\nYour 50,000-paper dataset is now ready for:")
print("  1. Data visualization")
print("  2. Trend analysis")
print("  3. FastAPI backend")
print("  4. MySQL database")
print("  5. Dashboard development")

print("\nDone!")