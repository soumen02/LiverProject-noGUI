# script that will generate the report and save it in the output folder

import os
import subprocess
import logging
import shutil
import sys
import SimpleITK as sitk
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
import SimpleITK as sitk
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import numpy as np


# Configure logging
dir_path = os.path.dirname(os.path.realpath(__file__))
log_file = os.path.join(dir_path, 'script.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

# get the output folder path
output_folder = sys.argv[1]

# get the dictionary of files
files = eval(sys.argv[2])

# print the dictionary of files
print(files)

# Dictionary format
# {
#     'Label Type': ('Path to the Volume File', 'Path to the Label File'),
# }


def plot_slices(sitk_image, filename):
    array_image = sitk.GetArrayFromImage(sitk_image)
    mid_slice_index = len(array_image) // 2  # get the middle slice
    plt.imsave(filename, array_image[mid_slice_index], cmap='gray')

def compute_volume(sitk_label):
    array_label = sitk.GetArrayFromImage(sitk_label)
    voxel_count = (array_label == 1).sum()
    voxel_volume = np.prod(sitk_label.GetSpacing())
    total_volume_mm3 = voxel_count * voxel_volume
    return total_volume_mm3

COLOR_MAP = {
    'Hepatic Artery': "Reds",
    'Portal Vein': "Greens",
    'Hepatic Vein': "Blues"
}

def extract_and_overlay_slices(volume, label, label_type):
    print(f"Processing label type: {label_type}")

    # Extract slices
    axial = volume[volume.shape[0]//2, :, :]
    coronal = volume[:, volume.shape[1]//2, :]
    sagittal = volume[:, :, volume.shape[2]//2]

    # Assuming `axial_slice` is the 2D numpy array representing an axial slice:
    axial = np.flip(axial, axis=1)  # This flips the image horizontally

    # For sagittal or coronal slices, if they appear flipped vertically:
    sagittal = np.flip(sagittal, axis=0)  # This flips the image vertically
    coronal = np.flip(coronal, axis=0)

    # Extract label slices
    axial_label = label[label.shape[0]//2, :, :]
    coronal_label = label[:, label.shape[1]//2, :]
    sagittal_label = label[:, :, label.shape[2]//2]

    fig, axs = plt.subplots(1, 3, figsize=(9, 3))

    # Overlay and plot
    axs[0].imshow(axial, cmap="gray")
    axs[0].imshow(np.ma.masked_where(axial_label == 0, axial_label), cmap=COLOR_MAP[label_type], alpha=0.8)

    axs[1].imshow(coronal, cmap="gray")
    axs[1].imshow(np.ma.masked_where(coronal_label == 0, coronal_label), cmap=COLOR_MAP[label_type], alpha=0.8)

    axs[2].imshow(sagittal, cmap="gray")
    axs[2].imshow(np.ma.masked_where(sagittal_label == 0, sagittal_label), cmap=COLOR_MAP[label_type], alpha=0.8)

    for ax in axs:
        ax.axis('off')

    output_path = f"temp_{label_type}.png"
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return output_path


def generate_pdf(output_folder, files):
    c = canvas.Canvas(os.path.join(output_folder, 'report.pdf'), pagesize=landscape(letter))
    width, height = landscape(letter)

    y_position = height - 1 * inch  # Start near the top of the page
    
    for label_type, (volume_file, label_file) in files.items():
        volume_image = sitk.GetArrayFromImage(sitk.ReadImage(volume_file))
        label_image = sitk.GetArrayFromImage(sitk.ReadImage(label_file))

        overlay_path = extract_and_overlay_slices(volume_image, label_image, label_type)

        # Add the overlay image to the PDF
        c.drawInlineImage(overlay_path, 1 * inch, y_position - 3*inch, width - 2*inch, 3*inch)
        y_position -= 3.5 * inch  # Shift downwards for the next image

        label_volume = compute_volume(sitk.ReadImage(label_file))
        text = f"Volume of {label_type}: {label_volume:.2f} mm^3"
        c.drawString(1 * inch, y_position, text)
        y_position -= 0.25 * inch  # Small shift for text

    c.save()

generate_pdf(output_folder, files)