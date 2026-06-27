import json
from pathlib import Path

RESULTS_DIR = Path("evaluation/results")

with open(
    RESULTS_DIR / "metrics.json",
    "r"
) as f:
    metrics = json.load(f)

report = []

report.append(
    "AI DRIVER MONITORING SYSTEM\n"
)

report.append(
    "=" * 50 + "\n"
)

for section, values in metrics.items():

    report.append(
        f"\n{section.upper()}\n"
    )

    report.append(
        "-" * 30 + "\n"
    )

    for key, value in values.items():

        report.append(
            f"{key}: {value}%\n"
        )

with open(
    RESULTS_DIR / "report.txt",
    "w"
) as f:

    f.writelines(report)

print(
    "Report generated successfully."
)