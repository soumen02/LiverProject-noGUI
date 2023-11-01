import os

# find the directory of the current file and store it in a variable

dir_path = os.path.dirname(os.path.realpath(__file__))

studiesHA = dir_path + "/StudiesHA" 
studiesPV = dir_path + "/StudiesPV"
studiesHV = dir_path + "/StudiesHV"

resultsHA = dir_path + "/StudiesHA/test_labels"
resultsPV = dir_path + "/StudiesPV/test_labels"
resultsHV = dir_path + "/StudiesHV/test_labels"

outputfolder = dir_path + "/Output"

mainHA = dir_path + "radiologyHA/main.py"
mainPV = dir_path + "radiologyPV/main.py"
mainHV = dir_path + "radiologyHV/main.py"

# run the three main files in sequence and wait for each to finish, also save the output in a log file while printing on the terminal
os.system("python3 " + mainHA)
os.system("python3 " + mainPV)
os.system("python3 " + mainHV)

# move only the contents of the three results folder to the output folder
os.system("mv " + resultsHA + "/* " + outputfolder)
os.system("mv " + resultsPV + "/* " + outputfolder)
os.system("mv " + resultsHV + "/* " + outputfolder)

# read the name of the files in the output folder and print them on the terminal
files = os.listdir(outputfolder)

# print the volumes of files in the output folder using fslstats and print them on the terminal
for file in files:
    print(file)
    os.system("fslstats " + outputfolder + "/" + file + " -V")

# Check if slicer is installed on the computer using which slicer command
# if slicer is installed then open both input files and output files in slicer using slicer command in the terminal 
# else print that slicer is not installed
if os.system("which slicer") == 0:
    os.system("slicer " + studiesHA + "/* " + studiesPV + "/* " + studiesHV + "/* " + outputfolder + "/*")
else:
    print("Slicer is not installed")


