import os
import subprocess
import logging

# Configure logging
dir_path = os.path.dirname(os.path.realpath(__file__))
log_file = os.path.join(dir_path, 'script.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

def get_path(dir_path, *args):
    return os.path.join(dir_path, *args)

def run_command(command):
    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            stdout, stderr = proc.communicate()
            if stdout:
                logging.info(stdout)
            if stderr:
                logging.error(stderr)
            if proc.returncode != 0:
                logging.error(f"Command '{' '.join(command)}' failed with error code: {proc.returncode}")
                exit(proc.returncode)
    except Exception as e:
        logging.error(f"Error executing command '{' '.join(command)}': {e}")
        exit(1)

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
