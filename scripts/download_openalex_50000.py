import requests
import pandas as pd
import os
import time
import math

# ============================================================
# OPENALEX 50,000 PUBLICATION DATASET
# Cursor Pagination Version
# ============================================================

TARGET_PAPERS = 50000

START_YEAR = 2015
END_YEAR = 2025

PAPERS_PER_REQUEST = 200

API_URL = "https://api.openalex.org/works"

# ------------------------------------------------------------
# Output path
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DATA_DIR, "openalex_50000.csv")


# ============================================================
# FUNCTIONS
# ============================================================

def get_year_targets(target, start_year, end_year):
    """
    Distribute the target number of papers as evenly as possible
    across the selected years.
    """

    years = list(range(start_year, end_year + 1))

    number_of_years = len(years)

    base = target // number_of_years
    remainder = target % number_of_years

    targets = {}

    for i, year in enumerate(years):

        if i < remainder:
            targets[year] = base + 1
        else:
            targets[year] = base

    return targets


def extract_work(work):
    """
    Convert an OpenAlex work record into a clean flat dictionary.
    """

    # --------------------------------------------------------
    # Authors
    # --------------------------------------------------------

    authors = []

    for author in work.get("authorships", []):

        author_info = author.get("author", {})

        author_name = author_info.get("display_name")

        if author_name:
            authors.append(author_name)

    authors_text = "; ".join(authors)


    # --------------------------------------------------------
    # Institutions
    # --------------------------------------------------------

    institutions = []

    for authorship in work.get("authorships", []):

        for institution in authorship.get("institutions", []):

            institution_name = institution.get("display_name")

            if institution_name:
                institutions.append(institution_name)

    # Remove duplicate institutions
    institutions = list(dict.fromkeys(institutions))

    institutions_text = "; ".join(institutions)


    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    topics = []

    for topic in work.get("topics", []):

        topic_name = topic.get("display_name")

        if topic_name:
            topics.append(topic_name)

    topics_text = "; ".join(topics)


    # --------------------------------------------------------
    # Primary topic
    # --------------------------------------------------------

    primary_topic = ""

    primary_topic_data = work.get("primary_topic")

    if isinstance(primary_topic_data, dict):

        primary_topic = primary_topic_data.get(
            "display_name",
            ""
        )


    # --------------------------------------------------------
    # Concepts
    # --------------------------------------------------------

    concepts = []

    for concept in work.get("concepts", []):

        concept_name = concept.get("display_name")

        if concept_name:
            concepts.append(concept_name)

    concepts_text = "; ".join(concepts)


    # --------------------------------------------------------
    # Location / Source
    # --------------------------------------------------------

    source_name = ""

    primary_location = work.get("primary_location")

    if isinstance(primary_location, dict):

        source = primary_location.get("source")

        if isinstance(source, dict):

            source_name = source.get(
                "display_name",
                ""
            )


    # --------------------------------------------------------
    # DOI
    # --------------------------------------------------------

    doi = work.get("doi")

    if doi is None:
        doi = ""


    # --------------------------------------------------------
    # Return cleaned record
    # --------------------------------------------------------

    return {

        "id": work.get("id", ""),

        "title": work.get("title", ""),

        "publication_year": work.get(
            "publication_year",
            ""
        ),

        "publication_date": work.get(
            "publication_date",
            ""
        ),

        "type": work.get(
            "type",
            ""
        ),

        "authors": authors_text,

        "institutions": institutions_text,

        "topics": topics_text,

        "primary_topic": primary_topic,

        "concepts": concepts_text,

        "cited_by_count": work.get(
            "cited_by_count",
            0
        ),

        "doi": doi,

        "source": source_name,

        "is_retracted": work.get(
            "is_retracted",
            False
        ),

        "open_access": work.get(
            "open_access",
            {}
        ).get(
            "is_oa",
            False
        )
    }


# ============================================================
# DOWNLOAD FUNCTION
# ============================================================

def download_year(year, target_count, overall_count):

    print()
    print("=" * 60)
    print(f"YEAR {year}")
    print("=" * 60)

    print(f"Target papers for {year}: {target_count}")

    collected = []

    cursor = "*"

    page_number = 0

    total_available = None


    while len(collected) < target_count:

        page_number += 1

        remaining = target_count - len(collected)

        per_page = min(
            PAPERS_PER_REQUEST,
            remaining
        )


        # ----------------------------------------------------
        # API parameters
        # ----------------------------------------------------

        params = {

            "filter": (
                f"from_publication_date:{year}-01-01,"
                f"to_publication_date:{year}-12-31"
            ),

            "per-page": per_page,

            "cursor": cursor,

            "select": (
                "id,title,publication_year,"
                "publication_date,type,authorships,"
                "topics,primary_topic,concepts,"
                "cited_by_count,doi,primary_location,"
                "is_retracted,open_access"
            )
        }


        print(
            f"Year {year} | "
            f"Request {page_number} | "
            f"Collected {len(collected)}/{target_count}"
        )


        # ----------------------------------------------------
        # API request
        # ----------------------------------------------------

        try:

            response = requests.get(
                API_URL,
                params=params,
                timeout=60
            )

        except requests.exceptions.RequestException as e:

            print()
            print("REQUEST ERROR:")
            print(e)

            print("Waiting 5 seconds and retrying...")

            time.sleep(5)

            page_number -= 1

            continue


        print(
            f"Status code: {response.status_code}"
        )


        # ----------------------------------------------------
        # Handle API errors
        # ----------------------------------------------------

        if response.status_code != 200:

            print()
            print("API ERROR:")
            print(response.text)

            print()
            print("Waiting 10 seconds before retry...")

            time.sleep(10)

            page_number -= 1

            continue


        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        data = response.json()


        if total_available is None:

            total_available = data.get(
                "meta",
                {}
            ).get(
                "count",
                0
            )

            print(
                f"Available publications in "
                f"{year}: {total_available:,}"
            )


        results = data.get(
            "results",
            []
        )


        # ----------------------------------------------------
        # No results
        # ----------------------------------------------------

        if not results:

            print(
                f"No more publications available "
                f"for {year}."
            )

            break


        # ----------------------------------------------------
        # Extract records
        # ----------------------------------------------------

        added = 0

        for work in results:

            record = extract_work(work)

            collected.append(record)

            added += 1

            if len(collected) >= target_count:

                break


        overall_count += added


        print(
            f"Added: {added} | "
            f"Year total: {len(collected)}/{target_count} | "
            f"Overall: {overall_count}/{TARGET_PAPERS}"
        )


        # ----------------------------------------------------
        # Get next cursor
        # ----------------------------------------------------

        meta = data.get(
            "meta",
            {}
        )

        next_cursor = meta.get(
            "next_cursor"
        )


        # ----------------------------------------------------
        # Stop if cursor unavailable
        # ----------------------------------------------------

        if not next_cursor:

            print(
                f"No next cursor available for {year}."
            )

            break


        # ----------------------------------------------------
        # Stop if cursor did not change
        # ----------------------------------------------------

        if next_cursor == cursor:

            print(
                "Cursor did not change. "
                "Stopping this year."
            )

            break


        cursor = next_cursor


        # ----------------------------------------------------
        # Small delay to be API friendly
        # ----------------------------------------------------

        time.sleep(0.15)


    print()
    print(
        f"YEAR {year} COMPLETE"
    )

    print(
        f"Collected: {len(collected)}/{target_count}"
    )

    return collected, overall_count


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("OPENALEX 50,000 PUBLICATION DATASET")
    print("CURSOR PAGINATION VERSION")
    print("=" * 60)

    print()
    print(f"Target: {TARGET_PAPERS}")
    print(f"Years: {START_YEAR} - {END_YEAR}")
    print(
        f"Papers per request: "
        f"{PAPERS_PER_REQUEST}"
    )

    # --------------------------------------------------------
    # Calculate target per year
    # --------------------------------------------------------

    year_targets = get_year_targets(
        TARGET_PAPERS,
        START_YEAR,
        END_YEAR
    )


    print()
    print("YEAR TARGETS")
    print("-" * 60)

    for year, target in year_targets.items():

        print(
            f"{year}: {target} papers"
        )


    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    all_records = []

    overall_count = 0


    for year in range(
        START_YEAR,
        END_YEAR + 1
    ):

        target_for_year = year_targets[year]


        # ----------------------------------------------------
        # Don't exceed global target
        # ----------------------------------------------------

        remaining_global = (
            TARGET_PAPERS -
            len(all_records)
        )

        if remaining_global <= 0:

            break


        target_for_year = min(
            target_for_year,
            remaining_global
        )


        # ----------------------------------------------------
        # Download year
        # ----------------------------------------------------

        year_records, overall_count = download_year(
            year,
            target_for_year,
            len(all_records)
        )


        all_records.extend(
            year_records
        )


        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        print()
        print(
            f"TOTAL COLLECTED: "
            f"{len(all_records):,}/"
            f"{TARGET_PAPERS:,}"
        )


    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    print()
    print("=" * 60)
    print("CREATING DATASET")
    print("=" * 60)


    if not all_records:

        print()
        print("ERROR: No records were downloaded.")

        return


    df = pd.DataFrame(
        all_records
    )


    print()
    print(
        f"Before duplicate removal: "
        f"{len(df):,}"
    )


    # --------------------------------------------------------
    # Remove duplicates by OpenAlex ID
    # --------------------------------------------------------

    if "id" in df.columns:

        df = df.drop_duplicates(
            subset=["id"]
        )


    print(
        f"After duplicate removal: "
        f"{len(df):,}"
    )


    # --------------------------------------------------------
    # If more than target, trim
    # --------------------------------------------------------

    if len(df) > TARGET_PAPERS:

        df = df.head(
            TARGET_PAPERS
        )


    # ========================================================
    # SORT DATASET
    # ========================================================

    if "publication_year" in df.columns:

        df = df.sort_values(
            by=[
                "publication_year",
                "id"
            ],
            ascending=[
                True,
                True
            ]
        )


    # ========================================================
    # RESET INDEX
    # ========================================================

    df = df.reset_index(
        drop=True
    )


    # ========================================================
    # SAVE DATASET
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # FINAL INFORMATION
    # ========================================================

    print()
    print("=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)

    print(
        f"Final dataset shape: "
        f"{df.shape}"
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )


    # ========================================================
    # COLUMNS
    # ========================================================

    print()
    print("COLUMNS")
    print("-" * 60)

    for i, column in enumerate(
        df.columns,
        start=1
    ):

        print(
            f"{i:2}. {column}"
        )


    # ========================================================
    # YEAR DISTRIBUTION
    # ========================================================

    print()
    print("YEAR DISTRIBUTION")
    print("-" * 60)

    if "publication_year" in df.columns:

        year_distribution = (
            df["publication_year"]
            .value_counts()
            .sort_index()
        )

        print(
            year_distribution
        )


    # ========================================================
    # DATASET INFORMATION
    # ========================================================

    print()
    print("DATASET INFORMATION")
    print("-" * 60)

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )


    # ========================================================
    # MISSING VALUES
    # ========================================================

    print()
    print("MISSING VALUES")
    print("-" * 60)

    missing = df.isnull().sum()

    print(
        missing[missing > 0]
    )


    # ========================================================
    # SAMPLE RECORDS
    # ========================================================

    print()
    print("SAMPLE RECORDS")
    print("-" * 60)

    print(
        df.head(3).to_string()
    )


    print()
    print("=" * 60)
    print("ALL DONE!")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()