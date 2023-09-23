import hub
import numpy as np
import tensorflow as tf
from keras.applications import MobileNetV2
from keras.layers import Dense, Flatten
from keras.models import Model
from keras.utils import to_categorical

# Parameters
input_shape = (96, 96, 3)  # Adjust this as needed
batch_size = 32
epochs = 10
num_classes = 2  # 'face' and 'not face'

# Load the AFW dataset
import deeplake
ds = deeplake.load("hub://activeloop/AFW")

tf_dataset = ds.tensorflow()
# Preprocess data
def map_data(sample):
    return {"input_1": sample['images']}, sample['keypoints']

tf_dataset = tf_dataset.map(map_data)


# Model Architecture
base_model = MobileNetV2(input_shape=input_shape, include_top=False, weights='imagenet')
x = base_model.output
x = Flatten()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# Compiling the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
print(next(iter(tf_dataset.batch(32)))[1].shape)

# Training the model
model.fit(tf_dataset.batch(32), epochs=epochs)

# Save the model
model.save('mobilenetv2_afw.h5')
