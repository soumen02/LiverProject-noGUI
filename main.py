import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

def get_path(dir_path, *args):
    return os.path.join(dir_path, *args)

def run_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=False)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{' '.join(command)}' failed with error:\n{e}\nOutput:\n{e.output}")
        exit(e.returncode)

def move_files(source, destination):
    if os.path.exists(source):
        run_command(["mv", source, destination])

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    paths = {
    "studiesHA": get_path(dir_path, "StudiesHA"),
    "studiesPV": get_path(dir_path, "StudiesPV"),
    "studiesHV": get_path(dir_path, "StudiesHV"),
    "resultsHA": get_path(dir_path, "StudiesHA", "test_labels"),
    "resultsPV": get_path(dir_path, "StudiesPV", "test_labels"),
    "resultsHV": get_path(dir_path, "StudiesHV", "test_labels"),
    "outputfolder": get_path(dir_path, "Output"),
    "mainHA": get_path(dir_path, "radiologyHA", "main.py"),
    "mainPV": get_path(dir_path, "radiologyPV", "main.py"),
    "mainHV": get_path(dir_path, "radiologyHV", "main.py")
}


    for key in ["mainHA", "mainPV", "mainHV"]:
        run_command(["python3", paths[key]])

    for key in ["resultsHA", "resultsPV", "resultsHV"]:
        move_files(paths[key], paths["outputfolder"])

    files = os.listdir(paths["outputfolder"])
    for file in files:
        logging.info(file)
        run_command(["fslstats", os.path.join(paths["outputfolder"], file), "-V"])

    if subprocess.run(["which", "slicer"], capture_output=True).returncode == 0:
        run_command(["slicer", paths["studiesHA"], paths["studiesPV"], paths["studiesHV"], paths["outputfolder"]])
    else:
        logging.warning("Slicer is not installed")

if __name__ == "__main__":
    main()
