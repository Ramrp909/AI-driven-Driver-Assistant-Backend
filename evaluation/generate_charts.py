import json
import os
import matplotlib.pyplot as plt

RESULTS_DIR = "evaluation/results"
CHART_DIR = os.path.join(
    RESULTS_DIR,
    "charts"
)

os.makedirs(
    CHART_DIR,
    exist_ok=True
)

with open(
    os.path.join(
        RESULTS_DIR,
        "metrics.json"
    ),
    "r"
) as f:

    metrics = json.load(f)

for section, values in metrics.items():

    labels = list(values.keys())
    scores = list(values.values())

    plt.figure(
        figsize=(8, 4)
    )

    plt.bar(
        labels,
        scores
    )

    plt.ylim(
        0,
        100
    )

    plt.title(
        f"{section.replace('_',' ').title()} Accuracy"
    )

    plt.xticks(
        rotation=20
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            CHART_DIR,
            f"{section}.png"
        )
    )

    plt.close()

print(
    "Charts generated successfully."
)