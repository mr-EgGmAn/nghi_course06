"""You are the manager of the company MedicStore that operates in Europe
Your boss, the CEO, asks you for a reporting in order to:
Analyze your sales, profit, profit per order, profit ratio, quantity from 2016 to 2020 and break by country
Monitor the discounts
Identify which subcategory have low profit ratio and high discount average
Shared with all company users through internet navigator / smartphone

Run it from the project root:

    uv run scripts/medicstore.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from openpyxl.drawing.image import Image

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "output_v3"


# --- Objective 1: consolidation ----------------------------------------------


def load_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the two parts of the sales and the mapping table."""
    part1 = pd.read_csv(data_dir / "Sales_MedicStore_part1.csv")
    part2 = pd.read_csv(data_dir / "Sales_MedicStore_part2.csv")
    mapping = pd.read_csv(data_dir / "Mapping.csv")
    return part1, part2, mapping


def consolidate(
    part1: pd.DataFrame, part2: pd.DataFrame, mapping: pd.DataFrame
) -> pd.DataFrame:
    """Concatenate the two parts, then merge them with the gender mapping table."""
    patients = pd.concat([part1, part2], ignore_index=True)
    df_final = patients.merge(mapping, on="gender_code", how="left")

    assert len(df_final) == len(patients), "The merge changed the number of lines"
    assert df_final["gender"].notna().all(), (
        "Some gender codes are not in the mapping table"
    )
    return df_final


# --- Objective 2: questions ----------------------------------------------------


def compute_shapes(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Technical Q1: number of lines and columns of each dataset."""
    return pd.DataFrame(
        {
            "dataset": list(datasets),
            "nb_lines": [df.shape[0] for df in datasets.values()],
            "nb_columns": [df.shape[1] for df in datasets.values()],
        }
    )


def prevalence_by(df: pd.DataFrame, column: str) -> pd.Series:
    """Prevalence of diabetes (mean of the 0/1 `diabetes` column) for each value of `column`."""
    return df.groupby(column)["diabetes"].mean()


def answer_business_questions(df: pd.DataFrame) -> dict[str, object]:
    """Business Q1 to Q8: return a dictionary {question: answer}."""
    by_gender = prevalence_by(df, "gender")
    age_by_diabetes = df.groupby("diabetes")["age"].mean()
    markers = df.groupby("diabetes")[["HbA1c_level", "blood_glucose_level"]].mean()
    by_hypertension = prevalence_by(df, "hypertension")
    by_smoking = prevalence_by(df, "smoking_history").sort_values(ascending=False)
    is_obese = df["bmi"] >= 30

    return {
        "How many patients were screened": len(df),
        "How many patients are diabetic": df["diabetes"].sum(),
        "What is the prevalence of diabetes": df["diabetes"].mean(),
        "What is the prevalence of diabetes for women": by_gender["Female"],
        "What is the prevalence of diabetes for men": by_gender["Male"],
        "What is the average age of diabetic patients": age_by_diabetes[1],
        "What is the average age of non-diabetic patients": age_by_diabetes[0],
        "What is the prevalence of diabetes for patients with BMI >= 30": df.loc[
            is_obese, "diabetes"
        ].mean(),
        "What is the prevalence of diabetes for patients with BMI < 30": df.loc[
            ~is_obese, "diabetes"
        ].mean(),
        "What is the average HbA1c_level of diabetic patients": markers.loc[
            1, "HbA1c_level"
        ],
        "What is the average HbA1c_level of non-diabetic patients": markers.loc[
            0, "HbA1c_level"
        ],
        "What is the average blood_glucose_level of diabetic patients": markers.loc[
            1, "blood_glucose_level"
        ],
        "What is the average blood_glucose_level of non-diabetic patients": markers.loc[
            0, "blood_glucose_level"
        ],
        "How many times higher is the prevalence with hypertension": by_hypertension[1]
        / by_hypertension[0],
        "Which smoking_history category has the highest prevalence": by_smoking.index[
            0
        ],
    }


# --- Objective 3: graphs -------------------------------------------------------


def save_bar_chart(series: pd.Series, title: str, path: Path) -> Path:
    """Save a bar chart of `series` as a PNG file."""
    fig, ax = plt.subplots()
    series.plot.bar(ax=ax, title=title, rot=0)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def save_histogram_by_diabetes(
    df: pd.DataFrame, column: str, title: str, path: Path
) -> Path:
    """Save the distribution of `column` for diabetic and non-diabetic patients as a PNG file."""
    fig, ax = plt.subplots()
    df.groupby("diabetes")[column].plot.hist(
        ax=ax, bins=40, alpha=0.5, density=True, legend=True
    )
    ax.set_title(title)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def make_graphs(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Create the 4 graphs of Objective 3 and return their paths."""
    return [
        save_bar_chart(
            df["gender"].value_counts(),
            "Number of patients per gender",
            output_dir / "patients_per_gender.png",
        ),
        save_bar_chart(
            prevalence_by(df, "gender"),
            "Prevalence of diabetes per gender",
            output_dir / "prevalence_per_gender.png",
        ),
        save_histogram_by_diabetes(
            df,
            "age",
            "Distribution of age (0 = non-diabetic, 1 = diabetic)",
            output_dir / "age_distribution.png",
        ),
        save_histogram_by_diabetes(
            df,
            "blood_glucose_level",
            "Distribution of blood glucose level (0 = non-diabetic, 1 = diabetic)",
            output_dir / "blood_glucose_distribution.png",
        ),
    ]


# --- Objective 4: export -------------------------------------------------------


def export_analysis(
    path: Path,
    df_shapes: pd.DataFrame,
    df_describe: pd.DataFrame,
    df_analysis: pd.DataFrame,
    graphs: list[Path],
) -> None:
    """Export the tables and the graphs into one Excel file, one sheet each."""
    with pd.ExcelWriter(path) as writer:
        df_shapes.to_excel(writer, sheet_name="technical_q1_shapes", index=False)
        df_describe.to_excel(writer, sheet_name="technical_q5_describe")
        df_analysis.to_excel(writer, sheet_name="business_questions", index=False)

        sheet = writer.book.create_sheet("graphs")
        for i, graph in enumerate(graphs):
            sheet.add_image(Image(graph), f"A{1 + 25 * i}")


# --- Pipeline ------------------------------------------------------------------


def main() -> None:
    """Run the whole pipeline: load, consolidate, analyse, export."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Objective 1
    part1, part2, mapping = load_data(DATA_DIR)
    df_final = consolidate(part1, part2, mapping)
    df_final.to_excel(OUTPUT_DIR / "diabetes_final.xlsx", index=False)

    # Objective 2
    df_shapes = compute_shapes(
        {
            "diabetes_part1.csv": part1,
            "diabetes_part2.csv": part2,
            "mapping.csv": mapping,
            "final dataset": df_final,
        }
    )
    df_describe = df_final.describe(include="all")
    # Duplicates are kept: without a patient identifier, two patients can share the same profile
    dict_analysis = {
        "How many lines are in diabetes_part1.csv": len(part1),
        "How many lines are in diabetes_part2.csv": len(part2),
        "How many lines are in mapping.csv": len(mapping),
        "How many lines are exact duplicates": df_final.duplicated().sum(),
        **answer_business_questions(df_final),
    }
    df_analysis = pd.DataFrame(
        list(dict_analysis.items()), columns=["Question", "Answer"]
    )

    # Objectives 3 and 4
    graphs = make_graphs(df_final, OUTPUT_DIR)
    export_analysis(
        OUTPUT_DIR / "diabetes_analysis.xlsx",
        df_shapes,
        df_describe,
        df_analysis,
        graphs,
    )

    print(df_analysis.to_string(index=False))
    print(f"\nAnalysis exported to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
