import os
import subprocess
import logging
import shutil

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

def move_and_rename_files(source_path, output_path, prefix, file_suffix='.nii.gz'):
    for filename in os.listdir(source_path):
        if filename.endswith(file_suffix):
            # Rename the file with the given prefix and move it to the output directory
            new_filename = prefix + filename
            shutil.move(os.path.join(source_path, filename), os.path.join(output_path, new_filename))

def get_nii_file(directory):
                for file in os.listdir(directory):
                    if file.endswith(".nii.gz"):
                        return file
                return None

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
    ### 
    # for key in ["mainHA", "mainPV", "mainHV"]:
    #     run_command(["python3", paths[key]])

    files = {'Hepatic Artery':(),
             'Portal Vein':(),
             'Hepatic Vein':()}
    
    for key in ["studiesHA", "studiesPV", "studiesHV"]:
        # move_and_rename_files(paths[key], paths["outputfolder"], 'volume_')
        pass
        
        if not os.path.exists(paths[key]):
            logging.error(f"Path {paths[key]} does not exist")
            exit(1)
        else:
            if key == "studiesHA":
                nii_file = get_nii_file(paths[key])
                if nii_file:
                    files['Hepatic Artery'] += (os.path.join(paths[key], nii_file),)
            elif key == "studiesPV":
                nii_file = get_nii_file(paths[key])
                if nii_file:
                    files['Portal Vein'] += (os.path.join(paths[key], nii_file),)
            elif key == "studiesHV":
                nii_file = get_nii_file(paths[key])
                if nii_file:
                    files['Hepatic Vein'] += (os.path.join(paths[key], nii_file),)

    for key in ["resultsHA", "resultsPV", "resultsHV"]:
        if not os.path.exists(paths[key]):
            logging.error(f"Path {paths[key]} does not exist")
            exit(1)
        else:
            move_and_rename_files(paths[key], paths["outputfolder"], 'label_')

            if key == "resultsHA":
                files['Hepatic Artery'] += (os.path.join(paths["outputfolder"], os.listdir(paths["outputfolder"])[0]),)
            elif key == "resultsPV":
                files['Portal Vein'] += (os.path.join(paths["outputfolder"], os.listdir(paths["outputfolder"])[0]),)
            elif key == "resultsHV":
                files['Hepatic Vein'] += (os.path.join(paths["outputfolder"], os.listdir(paths["outputfolder"])[0]),)

    # call reportscript.py to generate the report on the generated output folder, pass the files dictionary as an argument
    run_command(["python3", get_path(dir_path, "reportscript.py"), paths["outputfolder"], str(files)])

    # files = os.listdir(paths["outputfolder"])
    # for file in files:
    #     logging.info(file)
    #     run_command(["fslstats", os.path.join(paths["outputfolder"], file), "-V"])

    # if subprocess.run(["which", "slicer"], capture_output=True).returncode == 0:
    #     run_command(["slicer", paths["outputfolder"]])
    # else:
    #     logging.warning("Slicer is not installed")

if __name__ == "__main__":
    main()