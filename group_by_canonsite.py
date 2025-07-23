import csv
from pymol import cmd, CmdException
from pathlib import Path

METADATA_FILE = Path("../../metadata.csv")
ALIGNED_FILES_DIR = Path("../../aligned_files")

# Read the metadata CSV
with open(METADATA_FILE, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    grouped = {}
    for i, row in enumerate(reader):
        group = row["CanonSites alias"]
        observation = row["Code"]
        grouped.setdefault(group, set())
        grouped[group].add(observation)

colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']

colors = colors*(len(grouped)//len(colors)+1)

for canonsite, color in zip(sorted(grouped), colors):
    observations = grouped[canonsite]

    group = canonsite.replace(" ", "").replace("/","_")

    count = 0

    for observation in observations:
        file = ALIGNED_FILES_DIR / observation / f"{observation}.sdf"

        try:
            cmd.load(file, observation)
            count += 1
        except CmdException:
            print("ERROR", file, "not found")
            continue

        cmd.group(group, observation)

    if count:
        cmd.color(color, f"{group} and elem C")
