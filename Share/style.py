from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


OUTPUT_DIR = Path("outputs")
PNG_DIR = OUTPUT_DIR / "png"
HTML_DIR = OUTPUT_DIR / "html"
CSV_DIR = OUTPUT_DIR / "csv"
REPORT_DIR = OUTPUT_DIR / "report"


SOURCE_COLORS = {
    "Georgia": "#1f77b4",
    "OASIS": "#2ca02c",
    "NCHS": "#9467bd"
}

COUNTY_COLORS = {
    "Fulton": "#003f5c",
    "DeKalb": "#2f9e44"
}

CHART_COLORS = [
    "#003f5c",
    "#2f9e44",
    "#f59f00",
    "#d9480f",
    "#7048e8",
    "#0ca678",
    "#e03131",
    "#1971c2"
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
