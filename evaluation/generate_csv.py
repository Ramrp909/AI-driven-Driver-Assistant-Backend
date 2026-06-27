import json
import csv
import os

RESULTS_DIR = "evaluation/results"

with open(
    os.path.join(RESULTS_DIR, "metrics.json"),
    "r"
) as f:
    metrics = json.load(f)

for section, values in metrics.items():

    csv_path = os.path.join(
        RESULTS_DIR,
        f"{section}_results.csv"
    )

    with open(
        csv_path,
        "w",
        newline=""
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "Category",
            "Accuracy (%)"
        ])

        for key, value in values.items():
            writer.writerow([
                key,
                value
            ])

print("CSV files generated successfully.")