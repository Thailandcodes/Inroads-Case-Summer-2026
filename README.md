# Atlanta Health EDA

## INROADS Summer 2026 Case Competition

### Team Members
- Thailand Griffith
- ___________________

---

# Project Overview

This project explores mortality trends in the Atlanta metropolitan area using three independent public health datasets.

Data Sources:

- Georgia Rankable Causes
- OASIS
- NCHS Rankable Causes

Counties:

- Fulton County
- DeKalb County

The goal is to identify similarities, differences, and trends between counties while comparing the consistency of multiple public health data sources.

---

# Folder Structure

```
AtlantaHealthEDA/

│
├── data/
│
├── outputs/
│   ├── png/
│   ├── html/
│   └── csv/
│
├── helpers.py
├── graphs.py
├── explore_oasis.py
├── requirements.txt
└── README.md
```

---

# Installing

Install the required packages.

```bash
pip install -r requirements.txt
```

---

# Running the Project

Run

```bash
python explore_oasis.py
```

The script will automatically

- Load all datasets
- Clean the data
- Normalize percentages
- Create graphs
- Create interactive dashboards
- Export CSV files
- Create a Share folder
- Create a ZIP archive for sharing

---

# Visualizations

The project creates:

## Overview

- Total Deaths by Source and County

---

## Demographics

- Age Distribution
- Race Distribution
- Sex Distribution

---

## Causes of Death

- Top Causes by Source
- Top Causes by County
- Heatmaps
- Interactive Charts

---

## Dashboard

A one-page dashboard combines several important visualizations into a single figure suitable for presentations.

---

# Output Files

PNG graphs

```
outputs/png/
```

Interactive HTML graphs

```
outputs/html/
```

CSV files

```
outputs/csv/
```

---

# Technologies Used

- Python
- Pandas
- Matplotlib
- Seaborn
- Plotly
- OpenPyXL

---

# Notes

The analysis automatically normalizes demographic data using percentages where appropriate.

Average (mean) values are shown on graphs whenever they improve interpretation.

Interactive Plotly visualizations are included for presentations and exploration.

---

# Future Improvements

Potential additions include

- Correlation heatmaps
- Animated visualizations
- Population-adjusted death rates
- Sankey diagrams
- Treemaps
- Radar charts
- Streamlit dashboard

---

Developed for the INROADS Summer 2026 Case Competition.