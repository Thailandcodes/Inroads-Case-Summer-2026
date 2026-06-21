
import matplotlib.pyplot as plt
import seaborn as sns

COLORS = {
    "blue": "#0B2E63",
    "green": "#2E7D32",
    "orange": "#F28E2B",
    "red": "#D64045",
    "purple": "#6F4E9B",
    "light_blue": "#7EB6E8",
    "gray": "#5F6B7A",
}

SOURCE_COLORS = {
    "Georgia": COLORS["blue"],
    "OASIS": COLORS["green"],
    "NCHS": COLORS["purple"],
}

COUNTY_COLORS = {
    "Fulton": COLORS["blue"],
    "DeKalb": COLORS["green"],
}

GROUP_COLORS = {
    "Georgia - Fulton": "#0B2E63",
    "Georgia - DeKalb": "#2E7D32",
    "OASIS - Fulton": "#7EB6E8",
    "OASIS - DeKalb": "#F28E2B",
    "NCHS - Fulton": "#6F4E9B",
    "NCHS - DeKalB": "#D64045",
    "NCHS - DeKalb": "#D64045",
}


def set_theme():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "figure.titlesize": 18,
    })


def label_bars(ax, kind="number"):
    for container in ax.containers:
        if kind == "percent":
            ax.bar_label(container, fmt="%.1f%%", fontsize=8, padding=3)
        elif kind == "money":
            ax.bar_label(container, fmt="$%.1fM", fontsize=8, padding=3)
        else:
            ax.bar_label(container, labels=[f"{v.get_height():,.0f}" for v in container], fontsize=8, padding=3)


def save_figure(fig, filename):
    fig.tight_layout()
    fig.savefig(f"outputs/png/{filename}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def clean_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
