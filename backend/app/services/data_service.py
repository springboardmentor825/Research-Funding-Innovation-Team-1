from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

# Project root:
# D:\publication_trend_analysis

BASE_DIR = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "openalex_50000_clean.csv"
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():
    """
    Load the cleaned OpenAlex 50,000 publication dataset.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATASET_PATH}"
        )

    return pd.read_csv(DATASET_PATH)


# ============================================================
# DATASET INFORMATION
# ============================================================

def get_dataset_info():
    """
    Return basic information about the dataset.
    """

    df = load_dataset()

    return {
        "total_publications": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist()
    }