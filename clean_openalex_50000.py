import pandas as pd
import os

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = r"D:\publication_trend_analysis\data\openalex_50000.csv"

OUTPUT_DIR = r"D:\publication_trend_analysis\data\processed"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "openalex_50000_clean.csv"
)

# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("OPENALEX 50,000 DATASET - CLEANING")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Original shape: {df.shape}")

# ============================================================
# BASIC INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("ORIGINAL DATASET INFORMATION")
print("=" * 70)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nColumns:")
for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")

# ============================================================
# REMOVE DUPLICATES
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATE CHECK")
print("=" * 70)

duplicates_before = df.duplicated().sum()

print(f"Duplicate rows found: {duplicates_before}")

if duplicates_before > 0:
    df = df.drop_duplicates()
    print(f"Removed: {duplicates_before}")
else:
    print("No duplicate rows found.")

# ============================================================
# REMOVE DUPLICATE OPENALEX IDS
# ============================================================

if "id" in df.columns:

    duplicate_ids = df["id"].duplicated().sum()

    print(f"\nDuplicate OpenAlex IDs: {duplicate_ids}")

    if duplicate_ids > 0:
        df = df.drop_duplicates(subset=["id"])
        print(f"Removed {duplicate_ids} duplicate IDs.")
    else:
        print("All OpenAlex IDs are unique.")

# ============================================================
# HANDLE MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUE CHECK")
print("=" * 70)

missing_values = df.isnull().sum()

print(missing_values)

# ------------------------------------------------------------
# Fill numeric missing values
# ------------------------------------------------------------

if "cited_by_count" in df.columns:
    df["cited_by_count"] = pd.to_numeric(
        df["cited_by_count"],
        errors="coerce"
    ).fillna(0)

# ------------------------------------------------------------
# Fill text columns
# ------------------------------------------------------------

text_columns = [
    "title",
    "authors",
    "institutions",
    "topics",
    "primary_topic",
    "concepts",
    "doi",
    "source"
]

for column in text_columns:

    if column in df.columns:
        df[column] = df[column].fillna("Unknown")

# ============================================================
# DATA TYPE CORRECTION
# ============================================================

print("\n" + "=" * 70)
print("DATA TYPE CORRECTION")
print("=" * 70)

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

# ============================================================
# YEAR VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("PUBLICATION YEAR VALIDATION")
print("=" * 70)

if "publication_year" in df.columns:

    invalid_years = df[
        ~df["publication_year"].between(2015, 2025)
    ]

    print(f"Records outside 2015-2025: {len(invalid_years)}")

    if len(invalid_years) > 0:

        print("\nRemoving records outside target period...")

        df = df[
            df["publication_year"].between(2015, 2025)
        ]

# ============================================================
# VALIDATE CITATION COUNTS
# ============================================================

print("\n" + "=" * 70)
print("CITATION COUNT VALIDATION")
print("=" * 70)

if "cited_by_count" in df.columns:

    negative_citations = (
        df["cited_by_count"] < 0
    ).sum()

    print(
        f"Negative citation counts: "
        f"{negative_citations}"
    )

    if negative_citations > 0:

        df.loc[
            df["cited_by_count"] < 0,
            "cited_by_count"
        ] = 0

# ============================================================
# BOOLEAN COLUMN NORMALIZATION
# ============================================================

print("\n" + "=" * 70)
print("BOOLEAN COLUMN VALIDATION")
print("=" * 70)

boolean_columns = [
    "is_retracted",
    "open_access"
]

for column in boolean_columns:

    if column in df.columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.lower()
            .map({
                "true": True,
                "false": False,
                "1": True,
                "0": False
            })
            .fillna(False)
        )

        print(f"{column}: normalized")

# ============================================================
# CLEAN TEXT COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("TEXT CLEANING")
print("=" * 70)

for column in text_columns:

    if column in df.columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
        )

        print(f"{column}: cleaned")

# ============================================================
# REMOVE COMPLETELY EMPTY RECORDS
# ============================================================

before_empty_removal = len(df)

df = df.dropna(
    how="all"
)

removed_empty = (
    before_empty_removal - len(df)
)

print(
    f"\nCompletely empty rows removed: "
    f"{removed_empty}"
)

# ============================================================
# SORT BY PUBLICATION YEAR
# ============================================================

if "publication_year" in df.columns:

    df = df.sort_values(
        by=["publication_year", "id"]
    ).reset_index(drop=True)

# ============================================================
# FINAL MISSING VALUE CHECK
# ============================================================

print("\n" + "=" * 70)
print("FINAL MISSING VALUE CHECK")
print("=" * 70)

final_missing = df.isnull().sum()

print(final_missing)

# ============================================================
# FINAL DUPLICATE CHECK
# ============================================================

print("\n" + "=" * 70)
print("FINAL DUPLICATE CHECK")
print("=" * 70)

print(
    f"Duplicate rows: "
    f"{df.duplicated().sum()}"
)

if "id" in df.columns:

    print(
        f"Duplicate OpenAlex IDs: "
        f"{df['id'].duplicated().sum()}"
    )

# ============================================================
# YEAR DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("YEAR DISTRIBUTION")
print("=" * 70)

if "publication_year" in df.columns:

    year_distribution = (
        df["publication_year"]
        .value_counts()
        .sort_index()
    )

    print(year_distribution)

# ============================================================
# DATASET SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL DATASET SUMMARY")
print("=" * 70)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nFinal columns:")

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")

# ============================================================
# SAVE CLEAN DATASET
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)

print(f"\nSaved cleaned dataset:")
print(OUTPUT_FILE)

print(f"\nFinal shape: {df.shape}")

print("\nDataset is ready for EDA and trend analysis.")