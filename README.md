# Atlanta Health EDA

## INROADS Summer 2026 Case Competition

This project analyzes mortality patterns in Fulton County and DeKalb County using Georgia Rankable Causes, OASIS, and NCHS datasets. It also analyzes education and SES vulnerability patterns to identify the communities most affected by major causes of death.

## Main Run Command

Install packages:

```bash
pip install -r requirements.txt
```

Run the full project:

```bash
python main.py
```

The older scripts can remain in the repository, but `main.py` is now the clean run file.

## Outputs

After running `main.py`, the project creates:

```text
outputs/png/       static dashboard images
outputs/html/      interactive dashboards and drilldowns
outputs/csv/       cleaned summary data
outputs/report/    metrics_report.md
```

## Main Dashboards

The project now creates fewer, cleaner dashboard files instead of dozens of repeated charts:

- `dashboard_demographics.png`
- `dashboard_health_burden.png`
- `dashboard_social_determinants.png`
- `dashboard_target_groups.png`
- `dashboard_market_opportunity.png` if market opportunity data exists

Interactive files are saved as HTML. The sunbursts are limited to top causes per group and shallow display depth so the labels do not become unreadable.

## Data Files Needed

Required mortality files:

```text
data/Georgia Rankable Causes Fulton and Dekalb 2024.xlsx
data/Oasis Rankable Causes Fulton and Dekalb 2024.xlsx
data/NCHS Rankable Causes Fulton and Dekalb 2024.xlsx
```

Required education and SES files:

```text
data/Georgia 2024.xlsx
data/Oasis 2024.xlsx
data/NCHS 2024.xlsx
```

Optional market file:

```text
outputs/csv/market_opportunity_summary.csv
```

If the optional market file exists, `main.py` adds a market opportunity dashboard and market metrics to the report.

## Code Structure

```text
main.py       runs the project in order
helpers.py    loads and cleans data
graphs.py     creates dashboards and interactive visuals
style.py      keeps colors, fonts, and labels consistent
report.py     creates the markdown metrics report
```

## Notes

- Values are normalized into percentages where appropriate.
- Labels are cleaned for presentation, so underscores and long technical labels are removed where possible.
- PNG dashboards are meant for slides.
- HTML files are meant for interactive exploration.
