import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# OPENALEX 50,000 - DATA VISUALIZATION
# ============================================================

print("\n" + "=" * 70)
print("OPENALEX 50,000 - DATA VISUALIZATION")
print("=" * 70)


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "analysis",
    "results"
)

PLOTS_DIR = os.path.join(
    BASE_DIR,
    "analysis",
    "visualization",
    "plots"
)

os.makedirs(PLOTS_DIR, exist_ok=True)


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def load_result(filename):
    path = os.path.join(RESULTS_DIR, filename)

    if not os.path.exists(path):
        print(f"WARNING: File not found: {filename}")
        return None

    return pd.read_csv(path)


def save_plot(filename):
    path = os.path.join(PLOTS_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {path}")


# ============================================================
# 1. PUBLICATION YEAR TREND
# ============================================================

print("\n1. PUBLICATION YEAR TREND")

df = load_result("publication_year_trend.csv")

if df is not None:

    plt.figure(figsize=(10, 6))

    plt.plot(
        df["publication_year"],
        df["publication_count"],
        marker="o",
        linewidth=2
    )

    plt.title(
        "Publication Trend by Year",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Publication Year")
    plt.ylabel("Number of Publications")

    plt.xticks(df["publication_year"])
    plt.grid(True, alpha=0.3)

    save_plot("01_publication_year_trend.png")


# ============================================================
# 2. PUBLICATION GROWTH
# ============================================================

print("\n2. PUBLICATION GROWTH")

df = load_result("publication_year_trend.csv")

if df is not None:

    growth = df.dropna(subset=["growth_percentage"])

    plt.figure(figsize=(10, 6))

    plt.bar(
        growth["publication_year"],
        growth["growth_percentage"]
    )

    plt.axhline(
        y=0,
        linewidth=1
    )

    plt.title(
        "Publication Growth Percentage by Year",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Publication Year")
    plt.ylabel("Growth Percentage (%)")

    plt.xticks(growth["publication_year"])

    save_plot("02_publication_growth.png")


# ============================================================
# 3. DOMAIN DISTRIBUTION
# ============================================================

print("\n3. DOMAIN DISTRIBUTION")

df = load_result("domain_distribution.csv")

if df is not None:

    plt.figure(figsize=(10, 6))

    plt.barh(
        df["domain"],
        df["publication_count"]
    )

    plt.title(
        "Research Publications by Domain",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Number of Publications")
    plt.ylabel("Research Domain")

    plt.gca().invert_yaxis()

    save_plot("03_domain_distribution.png")


# ============================================================
# 4. DOMAIN TREND BY YEAR
# ============================================================

print("\n4. DOMAIN TREND BY YEAR")

df = load_result("domain_year_trend.csv")

if df is not None:

    pivot = df.pivot(
        index="publication_year",
        columns="domain",
        values="publication_count"
    )

    plt.figure(figsize=(12, 7))

    for domain in pivot.columns:
        plt.plot(
            pivot.index,
            pivot[domain],
            marker="o",
            label=domain
        )

    plt.title(
        "Research Domain Trends (2015-2025)",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Publication Year")
    plt.ylabel("Number of Publications")

    plt.legend()
    plt.grid(True, alpha=0.3)

    save_plot("04_domain_year_trend.png")


# ============================================================
# 5. TOP 20 RESEARCH TOPICS
# ============================================================

print("\n5. TOP 20 RESEARCH TOPICS")

df = load_result("topic_distribution.csv")

if df is not None:

    top20 = df.head(20).sort_values(
        "publication_count"
    )

    plt.figure(figsize=(12, 9))

    plt.barh(
        top20["topic"],
        top20["publication_count"]
    )

    plt.title(
        "Top 20 Research Topics",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Number of Publications")
    plt.ylabel("Research Topic")

    save_plot("05_top_20_topics.png")


# ============================================================
# 6. TOP 20 AUTHORS
# ============================================================

print("\n6. TOP 20 AUTHORS")

df = load_result("author_productivity.csv")

if df is not None:

    df = df[df["author"] != "Unknown"]

    top20 = df.head(20).sort_values(
        "publication_count"
    )

    plt.figure(figsize=(12, 9))

    plt.barh(
        top20["author"],
        top20["publication_count"]
    )

    plt.title(
        "Top 20 Authors by Publication Count",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Number of Publications")
    plt.ylabel("Author")

    save_plot("06_top_20_authors.png")


# ============================================================
# 7. TOP 20 INSTITUTIONS
# ============================================================

print("\n7. TOP 20 INSTITUTIONS")

df = load_result("institution_productivity.csv")

if df is not None:

    df = df[df["institution"] != "Unknown"]

    top20 = df.head(20).sort_values(
        "publication_count"
    )

    plt.figure(figsize=(12, 9))

    plt.barh(
        top20["institution"],
        top20["publication_count"]
    )

    plt.title(
        "Top 20 Institutions by Publication Count",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Number of Publications")
    plt.ylabel("Institution")

    save_plot("07_top_20_institutions.png")


# ============================================================
# 8. TOP 20 JOURNALS / SOURCES
# ============================================================

print("\n8. TOP 20 JOURNALS / SOURCES")

df = load_result("source_distribution.csv")

if df is not None:

    df = df[df["source"] != "Unknown"]

    top20 = df.head(20).sort_values(
        "publication_count"
    )

    plt.figure(figsize=(12, 9))

    plt.barh(
        top20["source"],
        top20["publication_count"]
    )

    plt.title(
        "Top 20 Publication Sources",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Number of Publications")
    plt.ylabel("Journal / Source")

    save_plot("08_top_20_sources.png")


# ============================================================
# 9. CITATION TREND
# ============================================================

print("\n9. CITATION TREND")

df = load_result("citation_trend.csv")

if df is not None:

    plt.figure(figsize=(11, 7))

    plt.plot(
        df["publication_year"],
        df["total_citations"],
        marker="o",
        linewidth=2,
        label="Total Citations"
    )

    plt.title(
        "Citation Trend by Publication Year",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Publication Year")
    plt.ylabel("Total Citations")

    plt.xticks(df["publication_year"])

    plt.grid(True, alpha=0.3)

    plt.legend()

    save_plot("09_citation_trend.png")


# ============================================================
# 10. AVERAGE CITATIONS BY YEAR
# ============================================================

print("\n10. AVERAGE CITATIONS")

df = load_result("citation_trend.csv")

if df is not None:

    plt.figure(figsize=(11, 7))

    plt.plot(
        df["publication_year"],
        df["average_citations"],
        marker="o",
        linewidth=2
    )

    plt.title(
        "Average Citations by Publication Year",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Publication Year")
    plt.ylabel("Average Citations")

    plt.xticks(df["publication_year"])

    plt.grid(True, alpha=0.3)

    save_plot("10_average_citations.png")


# ============================================================
# 11. OPEN ACCESS DISTRIBUTION
# ============================================================

print("\n11. OPEN ACCESS DISTRIBUTION")

df = load_result("open_access_distribution.csv")

if df is not None:

    plt.figure(figsize=(8, 8))

    plt.pie(
        df["publication_count"],
        labels=df["open_access"].map(
            {True: "Open Access", False: "Not Open Access"}
        ),
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(
        "Open Access vs Non-Open Access Publications",
        fontsize=16,
        fontweight="bold"
    )

    save_plot("11_open_access_distribution.png")


# ============================================================
# 12. OPEN ACCESS TREND
# ============================================================

print("\n12. OPEN ACCESS TREND")

df = load_result("open_access_year_trend.csv")

if df is not None:

    # Automatically detect percentage column
    percentage_columns = [
        col for col in df.columns
        if "percentage" in col.lower()
    ]

    if percentage_columns:

        percentage_col = percentage_columns[0]

        plt.figure(figsize=(11, 7))

        for value in df["open_access"].unique():

            subset = df[
                df["open_access"] == value
            ]

            label = (
                "Open Access"
                if value is True
                else "Not Open Access"
            )

            plt.plot(
                subset["publication_year"],
                subset[percentage_col],
                marker="o",
                label=label
            )

        plt.title(
            "Open Access Trend by Year",
            fontsize=16,
            fontweight="bold"
        )

        plt.xlabel("Publication Year")
        plt.ylabel("Percentage (%)")

        plt.xticks(
            sorted(df["publication_year"].unique())
        )

        plt.legend()
        plt.grid(True, alpha=0.3)

        save_plot("12_open_access_year_trend.png")


# ============================================================
# 13. RETRACTION DISTRIBUTION
# ============================================================

print("\n13. RETRACTION DISTRIBUTION")

df = load_result("retraction_distribution.csv")

if df is not None:

    plt.figure(figsize=(8, 8))

    plt.pie(
        df["publication_count"],
        labels=df["is_retracted"].map(
            {
                True: "Retracted",
                False: "Not Retracted"
            }
        ),
        autopct="%1.2f%%",
        startangle=90
    )

    plt.title(
        "Retracted vs Non-Retracted Publications",
        fontsize=16,
        fontweight="bold"
    )

    save_plot("13_retraction_distribution.png")


# ============================================================
# 14. PUBLICATION TYPES
# ============================================================

print("\n14. PUBLICATION TYPES")

df = load_result("publication_type_distribution.csv")

if df is not None:

    df = df.sort_values(
        "publication_count"
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        df["publication_type"],
        df["publication_count"]
    )

    plt.title(
        "Publication Types",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Number of Publications")
    plt.ylabel("Publication Type")

    save_plot("14_publication_types.png")


# ============================================================
# 15. DOI AVAILABILITY
# ============================================================

print("\n15. DOI AVAILABILITY")

df = load_result("doi_distribution.csv")

if df is not None:

    plt.figure(figsize=(8, 8))

    plt.pie(
        df["publication_count"],
        labels=df["doi_available"].map(
            {
                True: "DOI Available",
                False: "DOI Not Available"
            }
        ),
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(
        "DOI Availability",
        fontsize=16,
        fontweight="bold"
    )

    save_plot("15_doi_availability.png")


# ============================================================
# 16. YEARLY SUMMARY - PUBLICATIONS AND CITATIONS
# ============================================================

print("\n16. YEARLY SUMMARY")

df = load_result("yearly_summary.csv")

if df is not None:

    fig, ax1 = plt.subplots(figsize=(12, 7))

    ax1.plot(
        df["publication_year"],
        df["publication_count"],
        marker="o",
        linewidth=2
    )

    ax1.set_xlabel("Publication Year")
    ax1.set_ylabel("Number of Publications")

    ax1.tick_params(axis="y")

    ax2 = ax1.twinx()

    ax2.plot(
        df["publication_year"],
        df["average_citations"],
        marker="s",
        linewidth=2
    )

    ax2.set_ylabel("Average Citations")

    plt.title(
        "Publications and Average Citations by Year",
        fontsize=16,
        fontweight="bold"
    )

    ax1.grid(True, alpha=0.3)

    save_plot("16_yearly_publications_vs_citations.png")


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("VISUALIZATION COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nAll visualization files are saved in:")

print(PLOTS_DIR)

print("\nGenerated charts:")

for filename in sorted(os.listdir(PLOTS_DIR)):

    if filename.endswith(".png"):
        print("  ✓", filename)

print("\nNext stage:")
print("  1. Review generated charts")
print("  2. Create visualization dashboard")
print("  3. Build FastAPI backend")
print("  4. Connect MySQL database")
print("  5. Connect frontend dashboard")

print("\nDone!")