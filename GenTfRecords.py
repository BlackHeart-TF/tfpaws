import tensorflow as tf
import json
from collections import defaultdict

def create_tf_example(image_entry):
    image_path = f"/coco/train/catpeople/{image_entry['file_name']}"
    image = tf.io.read_file(image_path)
    image = tf.image.decode_jpeg(image)
    
    bboxes = image_entry['bboxes']
    class_ids = image_entry['class_ids']
    
    feature = {
        'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image.numpy().tobytes()])),
        'bbox': tf.train.Feature(float_list=tf.train.FloatList(value=bboxes)),
        'class': tf.train.Feature(int64_list=tf.train.Int64List(value=class_ids)),
    }
    
    example = tf.train.Example(features=tf.train.Features(feature=feature))
    return example.SerializeToString()

# Load JSON data
with open('/coco/filtered_annotations.json') as f:
    data = json.load(f)

# Organize data
image_data = defaultdict(lambda: {'bboxes': [], 'class_ids': []})
for annotation in data['annotations']:
    image_data[annotation['image_id']]['bboxes'].extend(annotation['bbox'])
    image_data[annotation['image_id']]['class_ids'].append(annotation['category_id'])

# Add image details
for img in data['images']:
    if img['id'] in image_data:
        image_data[img['id']].update(img)

# Write TFRecord
with tf.io.TFRecordWriter('/home/noire/output.tfrecord') as writer:
    for img_id, img_entry in image_data.items():
        example = create_tf_example(img_entry)
        writer.write(example)
