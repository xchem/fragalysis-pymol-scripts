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

for canonsite, observations in grouped.items():
    for observation in observations:
        file = ALIGNED_FILES_DIR / observation / f"{observation}.sdf"

        try:
            cmd.load(file, observation)
        except CmdException:
            print("ERROR", file, "not found")
            continue

        cmd.group(canonsite, observation)
