# MedicStore analysis

Analysis of MedicStore sales in Europe for 2016–2020. The project consolidates
two sales exports with a sub-category mapping, calculates sales indicators, and
exports tables and charts for review.

## Objectives

- Consolidate the two sales files and enrich them with category information.
- Analyse sales, quantity, orders, and customer activity by country and category.
- Monitor discounts and identify sub-categories with lower profitability.
- Produce Excel reports and visualisations that can be shared with the team.

## Project structure

```text
data/          Source CSV and Excel files, plus the merged dataset
exported_file/ Generated Excel reports and PNG charts
notebooks/     Exploratory analysis and reporting notebook
scripts/       Data download and analysis scripts
src/           Python package source
```

## Requirements

- Python 3.14 or later
- [uv](https://docs.astral.sh/uv/)

Install the locked dependencies from the project root:

```powershell
uv sync
```

## Usage

The completed analysis is available in
[`notebooks/medicstore_nb1.ipynb`](notebooks/medicstore_nb1.ipynb). Open it in
Jupyter or VS Code and run the cells from top to bottom:

```powershell
uv run jupyter notebook notebooks/medicstore_nb1.ipynb
```

The notebook reads the files in `data/` and writes reports to
`exported_file/`. It expects the sales CSV files to use semicolons as their
separator.

To download a fresh copy of the source data:

```powershell
uv run scripts/download_data.py
```

The downloader saves files in `data/` and overwrites files with matching names.
Use it only when you want to refresh the local source data.

## Inputs

- `Sales_MedicStore_part1.csv` and `Sales_MedicStore_part2.csv`: sales records.
- `Mapping.xlsx`: mapping from `Sub-Category` to `Category`.

## Outputs

- `exported_file/final_dataset1.xlsx`: consolidated dataset with calculated
  fields.
- `exported_file/medicstore_analysis.xlsx`: consolidated dataset, technical
  questions, business questions, and embedded charts.
- `exported_file/Number_of_orders_per_Category.png`: orders by category.
- `exported_file/Number_of_orders_per_Sub_Category.png`: orders by
  sub-category.

## Notes

The notebook is the primary end-to-end reporting workflow. The package entry
point currently contains only the default project template greeting, while
`scripts/medicstore.py` contains work-in-progress consolidation code.