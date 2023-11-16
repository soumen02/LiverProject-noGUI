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

def validate_files_dict(files):
    for key, value in files.items():
        if not value:
            logging.error(f"No files found for {key}.")
            return False
    return True

def get_nii_file(directory):
                for file in os.listdir(directory):
                    if file.endswith(".nii.gz"):
                        return file
                return None

def gather_files(path_key, result_key, label, paths, files):
    # Ensure the paths exist
    if not os.path.exists(paths[path_key]):
        logging.error(f"Path {paths[path_key]} does not exist")
        exit(1)
    if not os.path.exists(paths[result_key]):
        logging.error(f"Path {paths[result_key]} does not exist")
        exit(1)
    
    # Get the .nii file for the study
    study_file = get_nii_file(paths[path_key])
    if not study_file:
        logging.error(f"No .nii.gz file found in {paths[path_key]}")
        return
    
    if study_file:
        study_filepath = os.path.join(paths[path_key], study_file)
        
        # Move and rename files
        move_and_rename_files(paths[result_key], paths["outputfolder"], 'label_')
        
        result_file = get_nii_file(paths[result_key])
        if not result_file:
            logging.error(f"No .nii.gz file found in {paths[result_key]}")
            return
        
        if result_file:
            result_filepath = os.path.join(paths[result_key], result_file)
            
            # Update the dictionary
            files[label] = (study_filepath, result_filepath)

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    ####

#     paths = {
#     "studiesHA": get_path(dir_path, "StudiesHA"),
#     "studiesPV": get_path(dir_path, "StudiesPV"),
#     "studiesHV": get_path(dir_path, "StudiesHV"),
#     "resultsHA": get_path(dir_path, "StudiesHA", "test_labels"),
#     "resultsPV": get_path(dir_path, "StudiesPV", "test_labels"),
#     "resultsHV": get_path(dir_path, "StudiesHV", "test_labels"),
#     "outputfolder": get_path(dir_path, "Output"),
#     "mainHA": get_path(dir_path, "radiologyHA", "main.py"),
#     "mainPV": get_path(dir_path, "radiologyPV", "main.py"),
#     "mainHV": get_path(dir_path, "radiologyHV", "main.py")
# }
    
#     # check the files in study and make sure they are all .nii.gz
#     # if its .dcm, convert it to .nii.gz using dcm2niix
#     # else if its .nii, leave it as is
#     # else if its neither, log error and exit

#     for directory in [paths["studiesHA"], paths["studiesPV"], paths["studiesHV"]]:
#         for file in os.listdir(directory):
#             if file.endswith(".dcm"):
#                 run_command(["dcm2niix", "-o", directory, "-f", "%p", directory])
#                 break
#             elif file.endswith(".nii"):
#                 break
#             else:
#                 logging.error(f"File {file} is not a .dcm or .nii file. Exiting.")
#                 exit(1)


 
    # for key in ["mainHA", "mainPV", "mainHV"]:
    #     run_command(["python3", paths[key]])

    # files = {'Hepatic Artery':(),
    #          'Portal Vein':(),
    #          'Hepatic Vein':()}
    
    # # Gather files for each phase
    # gather_files("studiesHA", "resultsHA", 'Hepatic Artery', paths, files)
    # gather_files("studiesPV", "resultsPV", 'Portal Vein', paths, files)
    # gather_files("studiesHV", "resultsHV", 'Hepatic Vein', paths, files)

    # if validate_files_dict(files):
    #     run_command(["python3", get_path(dir_path, "reportscript.py"), paths["outputfolder"], str(files)])
    # else:
    #     logging.error("Not all required files were found. Exiting.")

    # ####

    files = {'Hepatic Artery':('/home/mri/soumen_fall2023/LiverApp_noGUI/Output/volume_10153545_HA-PVreg.nii.gz', '/home/mri/soumen_fall2023/LiverApp_noGUI/Output/label_volume_10153545_HA-PVreg.nii.gz'),
                'Portal Vein':('/home/mri/soumen_fall2023/LiverApp_noGUI/Output/volume_10153545_PV-PVreg.nii.gz', '/home/mri/soumen_fall2023/LiverApp_noGUI/Output/label_volume_10153545_PV-PVreg.nii.gz'),
                'Hepatic Vein':('/home/mri/soumen_fall2023/LiverApp_noGUI/Output/volume_10153545_HV-PVreg.nii.gz', '/home/mri/soumen_fall2023/LiverApp_noGUI/Output/label_volume_10153545_HV-PVreg.nii.gz')
                }
    
    run_command(["python3", get_path(dir_path, "reportscript.py"), '/home/mri/soumen_fall2023/LiverApp_noGUI/Output', str(files)])
    





if __name__ == "__main__":
    main()