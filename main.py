import os

studiesHA = "/home/mri/soumen_fall2023/LiverApp_noGUI/StudiesHA"
studiesPV = "/home/mri/soumen_fall2023/LiverApp_noGUI/StudiesPV"
studiesHV = "/home/mri/soumen_fall2023/LiverApp_noGUI/StudiesHV"

resultsHA = "/home/mri/soumen_fall2023/LiverApp_noGUI/StudiesPV/test_labels"
resultsPV = "/home/mri/soumen_fall2023/LiverApp_noGUI/StudiesHA/test_labels"
resultsHV = "/home/mri/soumen_fall2023/LiverApp_noGUI/StudiesHV/test_labels"

outputfolder = "/home/mri/soumen_fall2023/LiverApp_noGUI/Output"

mainHA = "/home/mri/soumen_fall2023/LiverApp_noGUI/radiologyHA/main.py"
mainPV = "/home/mri/soumen_fall2023/LiverApp_noGUI/radiologyPV/main.py"
mainHV = "/home/mri/soumen_fall2023/LiverApp_noGUI/radiologyHV/main.py"

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