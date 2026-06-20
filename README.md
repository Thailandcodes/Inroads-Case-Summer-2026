# Atlanta Health EDA

## INROADS Summer 2026 Case Competition

### Project Overview

This project explores mortality trends in Fulton County and DeKalb County using public health datasets from three sources:

* Georgia Rankable Causes
* OASIS
* NCHS Rankable Causes

The project also analyzes social determinant patterns using education level and SES vulnerability data. The goal is to identify which populations are most affected by major causes of death and how those patterns differ by county, source, race, sex, education, and economic vulnerability.

---

## Project Questions

This analysis focuses on:

* Which causes of death are most common in Fulton and DeKalb?
* How do mortality patterns differ by race and sex?
* Which education levels are most affected by specific causes of death?
* Which SES vulnerability levels are most affected by specific causes of death?
* How does race fit into education and SES mortality patterns?

---

## Folder Structure

```text
AtlantaHealthEDA/
│
├── data/
│   ├── Georgia Rankable Causes Fulton and Dekalb 2024.xlsx
│   ├── Oasis Rankable Causes Fulton and Dekalb 2024.xlsx
│   ├── NCHS Rankable Causes Fulton and Dekalb 2024.xlsx
│   ├── Georgia 2024.xlsx
│   ├── Oasis 2024.xlsx
│   └── NCHS 2024.xlsx
│
├── outputs/
│   ├── png/
│   ├── html/
│   └── csv/
│
├── explore_oasis.py
├── helpers.py
├── graphs.py
├── requirements.txt
└── README.md
```

---

## Technologies Used

* Python
* Pandas
* OpenPyXL
* Matplotlib
* Seaborn
* Plotly

---

## Installation

First, clone or open the project folder.

Then install the required packages:

```bash
pip install -r requirements.txt
```

---

## How to Run

Run the main analysis file:

```bash
python explore_oasis.py
```

The program will automatically:

* Create output folders
* Load all Excel datasets
* Clean the data
* Normalize values into percentages where appropriate
* Save cleaned CSV files
* Generate PNG and SVG charts
* Generate interactive HTML charts
* Create a `Share/` folder
* Create a shareable ZIP file called `AtlantaHealthEDA.zip`

---

## Output Files

Static charts are saved here:

```text
outputs/png/
```

Interactive charts are saved here:

```text
outputs/html/
```

Cleaned CSV files are saved here:

```text
outputs/csv/
```

The final shareable package is saved as:

```text
AtlantaHealthEDA.zip
```

---

## Main Visualizations

The project generates:

* Sex distribution by source and county
* Race distribution by source and county
* Top causes of death heatmaps
* Pie charts for sex, race, and causes of death
* Education level by cause of death heatmaps
* SES vulnerability by cause of death heatmaps
* Race + education + cause mortality rankings
* Race + SES vulnerability + cause mortality rankings
* Interactive sunburst charts for education, SES, race, and cause of death

---

## Notes

The analysis uses percentages when comparing groups across counties or sources so that results are easier to compare.

The interactive HTML files are useful for exploring the data more deeply and can be opened directly in a browser.

---

## Developed For

INROADS Summer 2026 Case Competition
