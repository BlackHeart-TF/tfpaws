import tensorflow as tf
import json

def create_tf_example(annotation, image_data):
    image_path = "/coco/train/catpeople/" + image_data[annotation['image_id']]['file_name']
    bbox = annotation['bbox']
    class_id = annotation['category_id']
    
    image = tf.io.read_file(image_path)
    image = tf.image.decode_jpeg(image)
    
    feature = {
        'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image.numpy().tobytes()])),
        'bbox': tf.train.Feature(float_list=tf.train.FloatList(value=bbox)),
        'class': tf.train.Feature(int64_list=tf.train.Int64List(value=[class_id])),
    }
    
    example = tf.train.Example(features=tf.train.Features(feature=feature))
    return example.SerializeToString()

# Load JSON data
with open('/coco/filtered_annotations.json') as f:
    data = json.load(f)

# Create a dictionary for image data for easy lookup
image_data = {img['id']: img for img in data['images']}

with tf.io.TFRecordWriter('/coco/output.tfrecord') as writer:
    for annotation in data['annotations']:
        example = create_tf_example(annotation, image_data)
        writer.write(example)
