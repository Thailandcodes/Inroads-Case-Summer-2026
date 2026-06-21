from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


OUTPUT_DIR = Path("outputs")
PNG_DIR = OUTPUT_DIR / "png"
HTML_DIR = OUTPUT_DIR / "html"
CSV_DIR = OUTPUT_DIR / "csv"
REPORT_DIR = OUTPUT_DIR / "report"


PRIMARY = "#C7462D"
SECONDARY = "#E87561"
ACCENT = "#F3B2A6"
DARK = "#3B0D0C"
MUTED = "#8C3B2E"
LIGHT = "#F9E7E2"

SOURCE_COLORS = {
    "Georgia": PRIMARY,
    "OASIS": SECONDARY,
    "NCHS": DARK
}

COUNTY_COLORS = {
    "Fulton": PRIMARY,
    "DeKalb": SECONDARY
}

CHART_COLORS = [
    PRIMARY,
    SECONDARY,
    ACCENT,
    DARK,
    MUTED,
    "#D95F45",
    "#F0A08E",
    "#6F1D1B"
]

FORECAST_COLORS = {
    "Conservative": "#E87561",
    "Base": "#C7462D",
    "Aggressive": "#3B0D0C"
}


def setup_chart_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 9
    plt.rcParams["figure.titlesize"] = 18
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.edgecolor"] = DARK
    plt.rcParams["axes.labelcolor"] = DARK
    plt.rcParams["xtick.color"] = DARK
    plt.rcParams["ytick.color"] = DARK
