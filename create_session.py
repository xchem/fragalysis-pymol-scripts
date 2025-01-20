import os
import shutil
import csv
from pymol import cmd

def apply_pymol_script(pdb_file):
    """Applies the specified PyMOL commands to the given PDB file."""
    cmd.load(pdb_file)
    cmd.hide("everything")
    cmd.bg_color("white")
    cmd.set("valence", 0)
    cmd.set("cartoon_side_chain_helper", 1)
    cmd.remove("RESNAME DMS+PEG+EDO+DTT+TCEP+MES+GOL+SO4+PO4+IPA+MPD")
    cmd.show("cartoon")
    cmd.color("grey90")
    cmd.show("stick", "organic")
    cmd.set("stick_radius", 0.175)
    cmd.show("spheres", "organic")
    cmd.set("sphere_scale", 0.2)
    cmd.color("yellow", "organic")
    cmd.color("atomic", "(not elem C)")
    cmd.show("stick", "br. all within 5 of organic")
    cmd.show("nb_spheres", "solvent within 3.5 of organic")
    cmd.show("surface")
    cmd.set("surface_color", "white")
    cmd.set("transparency", 0.25)

# File and directory paths
metadata_file = "metadata.csv"
aligned_files_dir = "aligned_files"
output_dir = "Renamed_pdbs"  # Output directory for renamed PDB files
log_file = os.path.join(output_dir, "missing_files.log")  # Log file inside the output directory
session_file = os.path.join(output_dir, "Pymol_session.pse")  # PyMOL session file in the output directory

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Open log file for writing
with open(log_file, "w") as log:
    log.write("Missing Directories or PDB Files Log\n")
    log.write("===============================\n")

    # Read the metadata CSV
    with open(metadata_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Ensure required columns exist
        fieldnames = reader.fieldnames
        if "Code" not in fieldnames or "Compound code" not in fieldnames:
            raise ValueError("CSV file must contain 'Code' and 'Compound code' columns.")

        # Start a new PyMOL session
        cmd.reinitialize()  # Reinitialize PyMOL to ensure a clean state
        print("Session file checked.")

        # Process each row in the metadata
        for row in reader:
            code = str(row["Code"].strip())
            compound_code = str(row["Compound code"].strip())

            # Locate the directory corresponding to `code`
            code_dir = os.path.join(aligned_files_dir, code)
            if not os.path.isdir(code_dir):
                log.write(f"Directory not found: {code_dir}\n")
                print(f"Directory not found: {code_dir}")
                continue

            # Locate the PDB file
            pdb_file = os.path.join(code_dir, f"{code}.pdb")
            if not os.path.isfile(pdb_file):
                log.write(f"PDB file not found: {pdb_file}\n")
                print(f"PDB file not found: {pdb_file}")
                continue

            # Generate the output file name
            output_pdb_file = os.path.join(output_dir, f"{compound_code}_{code}.pdb")

            # Copy the PDB file to the output directory with the new name if needed
            if not os.path.isfile(output_pdb_file):
                shutil.copy(pdb_file, output_pdb_file)
                print(f"Copied: {pdb_file} to {output_pdb_file}")

            # Open the PDB file in PyMOL and apply the script
            try:
                apply_pymol_script(output_pdb_file)
            except Exception as e:
                log.write(f"Error applying PyMOL script to {output_pdb_file}: {e}\n")
                print(f"Error applying PyMOL script to {output_pdb_file}: {e}")
                continue

            # Check if the object is already loaded
            object_name = f"{compound_code}_{code}"  # Unique name for each object
            if object_name not in cmd.get_names():
                # Load the PDB file if it is not already in the session
                cmd.load(output_pdb_file, object_name)
                print(f"Loaded: {output_pdb_file} into session with object name: {object_name}")

        # Save the PyMOL session
        try:
            cmd.save(session_file)
            print(f"PyMOL session file saved: {session_file}")
        except Exception as e:
            log.write(f"Failed to save PyMOL session: {e}\n")
            print(f"Failed to save PyMOL session: {e}")

    print(f"Process completed. Check the log and session files in the {output_dir} directory.")