import os
import pandas as pd
from sqlalchemy import text

from database import engine
from models import Publication


# ============================================================
# OPENALEX 50,000 - IMPORT DATA INTO MYSQL
# ============================================================

print("\n" + "=" * 70)
print("OPENALEX 50,000 - MYSQL DATA IMPORT")
print("=" * 70)


# ------------------------------------------------------------
# PATH TO CLEANED CSV
# ------------------------------------------------------------

CSV_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "data",
        "processed",
        "openalex_50000_clean.csv"
    )
)

print("\nCSV file:")
print(CSV_PATH)


# ------------------------------------------------------------
# CHECK FILE
# ------------------------------------------------------------

if not os.path.exists(CSV_PATH):
    print("\nERROR: Cleaned CSV file was not found.")
    raise SystemExit(1)

print("\nCSV file found successfully.")


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

print("\nLoading dataset...")

df = pd.read_csv(CSV_PATH)

print("Dataset loaded successfully.")
print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")


# ------------------------------------------------------------
# VERIFY COLUMNS
# ------------------------------------------------------------

required_columns = [
    "id",
    "title",
    "publication_year",
    "publication_date",
    "type",
    "authors",
    "institutions",
    "topics",
    "primary_topic",
    "concepts",
    "cited_by_count",
    "doi",
    "source",
    "is_retracted",
    "open_access"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nERROR: Missing columns:")
    for column in missing_columns:
        print(" -", column)

    raise SystemExit(1)

print("\nAll required columns are present.")


# ------------------------------------------------------------
# SELECT REQUIRED COLUMNS
# ------------------------------------------------------------

df = df[required_columns].copy()


# ------------------------------------------------------------
# CLEAN DATE COLUMN
# ------------------------------------------------------------

print("\nProcessing publication dates...")

df["publication_date"] = pd.to_datetime(
    df["publication_date"],
    errors="coerce"
).dt.date


# ------------------------------------------------------------
# CLEAN INTEGER COLUMN
# ------------------------------------------------------------

df["publication_year"] = pd.to_numeric(
    df["publication_year"],
    errors="coerce"
).astype("Int64")

df["cited_by_count"] = pd.to_numeric(
    df["cited_by_count"],
    errors="coerce"
).fillna(0).astype(int)


# ------------------------------------------------------------
# CLEAN BOOLEAN COLUMNS
# ------------------------------------------------------------

def convert_to_bool(value):

    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    value = str(value).strip().lower()

    return value in [
        "true",
        "1",
        "yes",
        "y"
    ]


df["is_retracted"] = df["is_retracted"].apply(
    convert_to_bool
)

df["open_access"] = df["open_access"].apply(
    convert_to_bool
)


# ------------------------------------------------------------
# REPLACE NaN VALUES
# ------------------------------------------------------------

text_columns = [
    "id",
    "title",
    "type",
    "authors",
    "institutions",
    "topics",
    "primary_topic",
    "concepts",
    "doi",
    "source"
]

for column in text_columns:

    df[column] = df[column].fillna("")


# ------------------------------------------------------------
# CONVERT DATAFRAME TO RECORDS
# ------------------------------------------------------------

records = df.to_dict(orient="records")

print("\nPrepared records:")
print(f"{len(records):,}")


# ------------------------------------------------------------
# IMPORT INTO MYSQL
# ------------------------------------------------------------

print("\nImporting data into MySQL...")
print("Please wait...")


try:

    with engine.begin() as connection:

        # Clear existing records.
        # This prevents duplicate data if the script is run again.
        connection.execute(
            text("DELETE FROM publications")
        )

        print("\nExisting records cleared.")

        # Insert records in batches.
        batch_size = 1000

        for start in range(
            0,
            len(records),
            batch_size
        ):

            batch = records[
                start:start + batch_size
            ]

            connection.execute(
                Publication.__table__.insert(),
                batch
            )

            imported = min(
                start + batch_size,
                len(records)
            )

            print(
                f"Imported {imported:,} / "
                f"{len(records):,}"
            )


    print("\n" + "=" * 70)
    print("MYSQL IMPORT COMPLETED SUCCESSFULLY")
    print("=" * 70)


except Exception as e:

    print("\n" + "=" * 70)
    print("MYSQL IMPORT FAILED")
    print("=" * 70)

    print("\nError:")
    print(e)

    raise SystemExit(1)


# ------------------------------------------------------------
# VERIFY RECORD COUNT
# ------------------------------------------------------------

print("\nVerifying MySQL record count...")

try:

    with engine.connect() as connection:

        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM publications"
            )
        )

        count = result.scalar()

    print(f"\nRecords in MySQL: {count:,}")

    if count == len(df):

        print("\n✓ Verification successful!")
        print(
            f"✓ All {count:,} publications "
            "were imported."
        )

    else:

        print("\nWARNING:")
        print(
            f"CSV records : {len(df):,}"
        )
        print(
            f"MySQL records: {count:,}"
        )


except Exception as e:

    print("\nVerification failed.")
    print(e)


print("\n" + "=" * 70)
print("IMPORT PROCESS FINISHED")
print("=" * 70)