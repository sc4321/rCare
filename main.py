import cv2
from ultralytics import YOLO
from threading import Thread
import threading

from VideoClipsRecord import videoClipsHandler
from send_data_to_app_via_firebase import FirebaseDB


# Define the threshold
THRESHOLD = 0.45

# Load the YOLOv8 model
model = YOLO("yolov8s.pt")
#model = YOLO("yolov8n.pt")

# Load the video
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(1)


# Creating an instance of videoClipsHandler
videoClipsHandlerInst = videoClipsHandler(r"C:\\projects\\check_clips_records")

config = {
    "apiKey": "AIzaSyCpWjvONF2eLfIxsFOKSJaM8oU4HvLiW-M",
    "authDomain": "480830608258-hsnsgpgooeov6v0cqdhcn5ba9ccqdg3g.apps.googleusercontent.com",
    "databaseURL": "https://remotecare-ce82a-default-rtdb.firebaseio.com",
    "storageBucket": "remotecare-ce82a.appspot.com",
    "serviceAccount": r"C:\\projects\\yolov8and_all_features_from_v7\\firebase-adminsdk-serviceAccount.json"
}

# Initialize FirebaseDB instance
firebase_db_Inst = FirebaseDB(config, "shlomocohen2@gmail.com", "ZCBMnvx1!")


def detect_person(frame):
    # Make a prediction
    detections = model(frame)

    # Filter out detections with a low confidence score
    filtered_detections = []
    for box in detections[0].boxes:
        if box.conf is not None and box.conf.numel() > 0:  # Check if probs is not None and not empty
            max_prob = box.conf.max().item()  # Get the maximum probability
            if max_prob >= THRESHOLD and box.cls[0] == 0:
                filtered_detections.append([box.xywh.tolist()[0], box.conf.max().item()])

    # Return the filtered detections
    return filtered_detections



image_counter = 0
# Loop over the frames in the video
while True:
    # Capture the next frame
    ret, frame = cap.read()
    # If the frame is empty, break out of the loop
    if not ret:
        break

    # Detect persons in the frame
    filtered_detections = detect_person(frame)

    # If no detections were found, rotate the image and try again
    '''
    if len(filtered_detections) == 0:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        filtered_detections = detect_person(frame)
    '''

    '''
    if len(filtered_detections) == 0:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        filtered_detections = detect_person(frame)
        #no persons found in 3 direction
        if len(filtered_detections) == 0:
            continue    
    '''
    # Draw bounding boxes around the filtered detections
    for detection in filtered_detections:
        confidence_score = detection[1]

        # Get the bounding box of the detection
        bounding_box = detection[0]  # bounding_box is a list of four floats: [x1, y1, w, h]

        # Convert the bounding box to two points
        top_left_x = int(bounding_box[0] - bounding_box[2] // 2)
        top_left_y = int(bounding_box[1] - bounding_box[3] // 2)
        bottom_right_x = int(bounding_box[0] + bounding_box[2] // 2)
        bottom_right_y = int(bounding_box[1] + bounding_box[3] // 2)

        # Draw a rectangle around the detection
        cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (255, 255, 255), 2)
        #cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 0), -1)

        # Print the confidence score of the detection over the screen
        cv2.putText(frame, f"{confidence_score:.2f}", (top_left_x, top_left_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # if needs to record frame, send to dedicated thread
    if True:
        # append image to clip
        t_writer = threading.Thread(target=videoClipsHandlerInst.thread_write_frame_out(frame))

    image_counter += 1
    img_name = str(image_counter)+'.jpg'
    firebase_db_Inst.firebase_admin_upload_np_image_to_storage(frame, img_name)

    # Display the frame
    cv2.imshow("Frame", frame)

    # Check for the "q" key to quit the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the video capture object and close the OpenCV window
cap.release()
cv2.destroyAllWindows()



# work 1 frame:
"""import cv2
from ultralytics import YOLO
import numpy as np

# Define the threshold
THRESHOLD = 0.1

# Load the YOLOv8 model
model = YOLO("yolov8s.pt")

# Load the image to be detected
# image = cv2.imread("image.jpg") # original
image = cv2.VideoCapture(0).read()[1]

# Make a prediction
detections = model(image)

# Filter out detections with a low confidence score
filtered_detections = []
for detection in detections:
    if detection.boxes.conf is not None:  # Check if probs is not None
        max_prob = detection.boxes.conf.max().item()  # Get the maximum probability
        if max_prob >= THRESHOLD:
            filtered_detections.append(detection)

# Check if there are any detections
if len(filtered_detections) > 0:
    # Draw bounding boxes around the filtered detections
    for detection in filtered_detections:
        bbox = detection.boxes.xywh  # Get the bounding box coordinates in xywh format
        bbox = bbox[0]
        x, y, w, h = np.array(bbox, dtype=int)

        # Convert the bounding box coordinates to the format [top_left_x, top_left_y, width, height]
        top_left_x = x - w // 2
        top_left_y = y - h // 2

        # Draw a bounding box around the detection
        cv2.rectangle(image, (top_left_x, top_left_y), (top_left_x + w, top_left_y + h), (0, 0, 255), 8)  # Top border - blue
        cv2.rectangle(image, (top_left_x, top_left_y + h), (top_left_x + w, top_left_y + h * 2), (0, 255, 0), 8)  # Right border - green
        cv2.rectangle(image, (top_left_x + w, top_left_y + h * 2), (top_left_x + w * 2, top_left_y + h * 2), (255, 255, 255), 8)  # Bottom border - red
        cv2.rectangle(image, (top_left_x + w * 2, top_left_y + h * 2), (top_left_x + w * 2, top_left_y), (0, 0, 255), 8)  # Left border - blue

        # Get the class probability for the detection
        class_prob = detection.boxes.conf[detection.boxes.cls.argmax().item()]

        # Display the class probability on the image
        text = f"{class_prob:.2f}"
        cv2.putText(image, text, (top_left_x, top_left_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Display the image
cv2.imshow("Image", image)
cv2.waitKey(0)
"""

# work 2 detect 1:
"""
import cv2
from ultralytics import YOLO

# Define the threshold
THRESHOLD = 0.4

# Load the YOLOv8 model
# model = YOLO("yolov8s.pt")
model = YOLO("yolov8n.pt")

# Load the video
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(1)


def detect_person(frame):
    # Make a prediction
    detections = model(frame)

    # Filter out detections with a low confidence score
    filtered_detections = []
    for detection in detections:
        if detection.boxes.conf is not None and detection.boxes.conf.numel() > 0:  # Check if probs is not None and not empty
            max_prob = detection.boxes.conf.max().item()  # Get the maximum probability
            if max_prob >= THRESHOLD and detection.cls == 0:
                filtered_detections.append([detection.boxes.xywh.tolist()[0], detection.boxes.conf.max().item()])

    # Return the filtered detections
    return filtered_detections


# Loop over the frames in the video
while True:
    # Capture the next frame
    ret, frame = cap.read()
    # If the frame is empty, break out of the loop
    if not ret:
        break

    # Detect persons in the frame
    filtered_detections = detect_person(frame)

    # If no detections were found, rotate the image and try again
    if len(filtered_detections) == 0:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        filtered_detections = detect_person(frame)
        #if len(filtered_detections) == 0:
        #    continue

    # Draw bounding boxes around the filtered detections
    for detection in filtered_detections:
        confidence_score = detection[1]

        # Get the bounding box of the detection
        bounding_box = detection[0]  # bounding_box is a list of four floats: [x1, y1, w, h]

        # Convert the bounding box to two points
        top_left_x = int(bounding_box[0] - bounding_box[2] // 2)
        top_left_y = int(bounding_box[1] - bounding_box[3] // 2)
        bottom_right_x = int(bounding_box[0] + bounding_box[2] // 2)
        bottom_right_y = int(bounding_box[1] + bounding_box[3] // 2)

        # Draw a rectangle around the detection
        cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 0), 2)

        # Print the confidence score of the detection over the screen
        cv2.putText(frame, f"{confidence_score:.2f}", (top_left_x, top_left_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Frame", frame)

    # Check for the "q" key to quit the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the video capture object and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
"""
