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
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image as ReportLabImage, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

from reportlab.platypus import Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# Configure logging
dir_path = os.path.dirname(os.path.realpath(__file__))
log_file = os.path.join(dir_path, 'script.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

# get the output folder path
output_folder = sys.argv[1]

# get the dictionary of files
files = eval(sys.argv[2])

# print the dictionary of files
logging.info("Files Dictionary", files)

# Dictionary format
# {
#     'Label Type': ('Path to the Volume File', 'Path to the Label File'),
# }

def resize_image(input_path, output_path, size):
    # 'size' is a tuple (width, height)
    image = Image.open(input_path)
    image = image.resize(size, Image.ANTIALIAS)
    image.save(output_path)

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

def extract_and_overlay_slices(volume, label, label_type, view):
    # Determine which slice to extract based on the view
    if view == 'axial':
        slice_idx = volume.shape[0] // 2
        slice = volume[slice_idx, :, :]
        label_slice = label[slice_idx, :, :]
    elif view == 'coronal':
        slice_idx = volume.shape[1] // 2
        slice = volume[:, slice_idx, :]
        label_slice = label[:, slice_idx, :]
    elif view == 'sagittal':
        slice_idx = volume.shape[2] // 2
        slice = volume[:, :, slice_idx]
        label_slice = label[:, :, slice_idx]
    else:
        raise ValueError(f"Unknown view type: {view}")

    # Flip the slices if necessary to match the desired radiological view
    slice = np.flip(slice, axis=0)
    label_slice = np.flip(label_slice, axis=0)

    # Overlay the label slice onto the image slice
    # Assuming label_slice is a binary mask where 1 indicates the label
    color_map = {
        'Hepatic Artery': 'Reds',
        'Portal Vein': 'Greens',
        'Hepatic Vein': 'Blues'
    }
    overlay_color = color_map.get(label_type, 'gray')

    plt.imshow(slice, cmap='gray')
    plt.imshow(np.ma.masked_where(label_slice == 0, label_slice), cmap=overlay_color, alpha=0.5)
    plt.axis('off')

    # Save the overlay image
    output_path = f"temp_{label_type}_{view}.png"
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return output_path


def generate_pdf(output_folder, files):
    doc = SimpleDocTemplate(os.path.join(output_folder, 'report.pdf'), pagesize=letter)
    elements = []

    # Define the image and table sizes
    image_width = 120  # Smaller width for images
    image_height = 120  # Smaller height for images
    table_width = doc.width/2.0  # Half the width of the page
    table_data = [['Phase', 'Volume (mm³)']]
    
    # Header
    elements.append(Paragraph('Triple Phase Liver CT Scan Report', getSampleStyleSheet()['Title']))
    elements.append(Spacer(1, 12))
    
    for label_type, (volume_file, label_file) in files.items():
        # Process the images and resize them
        volume_image = sitk.GetArrayFromImage(sitk.ReadImage(volume_file))
        label_image = sitk.GetArrayFromImage(sitk.ReadImage(label_file))

        # Generate and save separate views for each phase
        views = ['axial', 'coronal', 'sagittal']
        image_paths = []

        for view in views:
            overlay_path = extract_and_overlay_slices(volume_image, label_image, label_type, view)
            resized_image_path = f"resized_{label_type}_{view}.png"
            resize_image(overlay_path, resized_image_path, size=(image_width, image_height))
            image_paths.append(resized_image_path)

        # Create the row with different views for each phase
        image_row = [ReportLabImage(path) for path in image_paths]
        elements.append(Table([image_row], colWidths=[image_width] * len(views), rowHeights=[image_height]))
        elements.append(Spacer(1, 12))  # Add some space between the image rows


        # Compute volume and add to the table data
        label_volume = compute_volume(sitk.ReadImage(label_file))
        table_data.append([label_type, f"{label_volume:.2f}"])
    
    # Create the table for volume data
    volume_table = Table(table_data, colWidths=[table_width/2.0] * 2)
    volume_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(volume_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph('Generated on: {}'.format(datetime.now().strftime('%Y-%m-%d')), getSampleStyleSheet()['Normal']))
    
    doc.build(elements)

generate_pdf(output_folder, files)
