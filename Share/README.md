# Atlanta Health EDA

## INROADS Summer 2026 Case Competition

This project analyzes health burden, social determinants, Aetna Medicare Advantage enrollment, age 65+ market opportunity, and CVS Health Care Benefits revenue trends for Fulton County and DeKalb County.

## Main Question

Which communities in Fulton and DeKalb show the strongest health burden, and where does CVS/Aetna have an opportunity to expand preventive care outreach?

## Sources Used

- Georgia Rankable Causes Fulton and DeKalb 2024
- OASIS Rankable Causes Fulton and DeKalb 2024
- NCHS Rankable Causes Fulton and DeKalb 2024
- Georgia, OASIS, and NCHS social determinants data
- CMS CPSC Medicare Advantage enrollment data
- U.S. Census ACS S0101 Age and Sex data
- CVS Health Care Benefits segment revenue data, 2023-2025

## Important Note About NCHS

NCHS is kept separate from Georgia and OASIS in combined visuals because its categories and structure are not directly comparable. The program generates separate NCHS charts.

## Project Structure

```text
AtlantaHealthEDA/
│
├── main.py
├── helpers.py
├── graphs.py
├── style.py
├── report.py
├── analyze_aetna_ma_enrollment.py
├── market_dashboards.py
├── forecast.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── Georgia Rankable Causes Fulton and Dekalb 2024.xlsx
│   ├── Oasis Rankable Causes Fulton and Dekalb 2024.xlsx
│   ├── NCHS Rankable Causes Fulton and Dekalb 2024.xlsx
│   ├── Georgia 2024.xlsx
│   ├── Oasis 2024.xlsx
│   ├── NCHS 2024.xlsx
│   ├── CPSC_Enrollment_Info_2026_01.csv
│   ├── ACSST1Y2024.S0101-2026-06-20T225846.csv
│   └── cvs_health_care_benefits_2023_2025.csv
│
└── outputs/
    ├── png/
    ├── html/
    ├── csv/
    └── report/
```

## Install Requirements

```bash
pip install -r requirements.txt
```

## Run Everything

```bash
python main.py
```

## Outputs

The program creates:

- Separate health burden heatmaps by source and county
- Combined Georgia/OASIS pie dashboards
- Separate NCHS pie dashboards
- Education and SES heatmaps
- Race + education and race + SES rankings
- Sunburst charts for Georgia/OASIS
- Separate NCHS sunburst charts
- Aetna enrollment chart
- Age 65+ market opportunity dashboard
- CVS Health Care Benefits forecast charts
- Aetna market opportunity revenue chart
- Markdown report with project metrics

The metrics report is saved here:

```text
outputs/report/metrics_report.md
```

## Run Individual Parts

```bash
python analyze_aetna_ma_enrollment.py
python market_dashboards.py
python forecast.py
```

Use `python main.py` for the final full analysis.
