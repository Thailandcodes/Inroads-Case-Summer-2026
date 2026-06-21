from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


OUTPUT_DIR = Path("outputs")
PNG_DIR = OUTPUT_DIR / "png"
HTML_DIR = OUTPUT_DIR / "html"
CSV_DIR = OUTPUT_DIR / "csv"
REPORT_DIR = OUTPUT_DIR / "report"


SOURCE_COLORS = {
    "Georgia": "#C7462D",
    "OASIS": "#E87561",
    "NCHS": "#3B0D0C"
}

COUNTY_COLORS = {
    "Fulton": "#C7462D",
    "DeKalb": "#E87561"
}

CHART_COLORS = [
    "#C7462D",
    "#E87561",
    "#F3B2A6",
    "#3B0D0C",
    "#8C3B2E",
    "#D95F45",
    "#F0A08E",
    "#6F1D1B"
]


def setup_chart_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 9
    plt.rcParams["figure.titlesize"] = 18
