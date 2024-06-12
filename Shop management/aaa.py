import cv2
import numpy as np
import tensorflow as tf

model = tf.keras.models.load_model('object_detection_model.h5')

class_names = ['class1', 'class2']

image_height = 224
image_width = 224

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    resized_frame = cv2.resize(frame, (image_width, image_height))

    normalized_frame = resized_frame / 255.0

    input_frame = np.expand_dims(normalized_frame, axis=0)

    predictions = model.predict(input_frame)

    predicted_box = predictions[0][:4](xmin, ymin, xmax, ymax)
    predicted_class = np.argmax(predictions[0][4:])
    predicted_label = class_names[predicted_class]

    h, w, _ = frame.shape
    xmin = int(predicted_box[0] * w)
    ymin = int(predicted_box[1] * h)
    xmax = int(predicted_box[2] * w)
    ymax = int(predicted_box[3] * h)

    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
    cv2.putText(frame, f'{predicted_label}', (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow('Object Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
