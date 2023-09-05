import json
import shutil
import os

# Load COCO annotations
with open("/coco/annotations/instances_train2017.json", "r") as f:
    data = json.load(f)

# Filtered data
filtered_data = {'images': [], 'annotations': [], 'categories': []}

# Filter categories
for category in data['categories']:
    if category['name'] in ['person', 'cat']:
        filtered_data['categories'].append(category)

# Filter images and annotations
for annotation in data['annotations']:
    if annotation['category_id'] in [cat['id'] for cat in filtered_data['categories']]:
        filtered_data['annotations'].append(annotation)
        img_id = annotation['image_id']
        img_data = [img for img in data['images'] if img['id'] == img_id][0]
        if img_data not in filtered_data['images']:
            filtered_data['images'].append(img_data)
            # Copy image to new directory
            print(img_data['file_name'])
            shutil.copy(f"/coco/train/train2017/{img_data['file_name']}", f"/coco/train/catpeople/{img_data['file_name']}")

# Save new JSON
with open("/coco/filtered_annotations.json", "w") as f:
    json.dump(filtered_data, f)
