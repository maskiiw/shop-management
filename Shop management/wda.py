import os
import cv2
import xml.etree.ElementTree as ET
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    image_path = os.path.join('dataset/images', root.find('filename').text)
    image = cv2.imread(image_path)

    boxes = []
    labels = []

    for obj in root.findall('object'):
        label = obj.find('name').text
        xmin = int(obj.find('bndbox').find('xmin').text)
        ymin = int(obj.find('bndbox').find('ymin').text)
        xmax = int(obj.find('bndbox').find('xmax').text)
        ymax = int(obj.find('bndbox').find('ymax').text)

        boxes.append([xmin, ymin, xmax, ymax])
        labels.append(label)

    return image, boxes, labels


data_dir = 'dataset/annotations'
xml_files = [file for file in os.listdir(data_dir) if file.endswith('.xml')]

images = []
labels_list = []
for xml_file in xml_files:
    image, boxes, labels = parse_xml(os.path.join(data_dir, xml_file))
    images.append(image)
    # استفاده از اولین برچسب هر تصویر
    labels_list.append(labels[0] if labels else 'unknown')  # در صورت عدم وجود برچسب

# تغییر اندازه تصاویر
image_height = 224
image_width = 224
resized_images = []
for image in images:
    resized_image = cv2.resize(image, (image_width, image_height))
    resized_images.append(resized_image)
images = np.array(resized_images)

# پردازش برچسب‌ها
le = LabelEncoder()
labels_array = le.fit_transform(labels_list)

num_classes = len(le.classes_)

# تعریف مدل
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(image_height, image_width, 3)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(num_classes, activation='softmax')])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# آموزش مدل
model.fit(images, labels_array, epochs=10)

# ذخیره مدل
model.save('object_detection_model.h5')
