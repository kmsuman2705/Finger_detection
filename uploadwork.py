#!/usr/bin/python3
import cgi
import cv2
import io
import numpy as np
import mediapipe as mp

print("Content-Type: text/html")
print()

def launch_os():
    try:
        import boto3
        ec2 = boto3.resource('ec2', region_name='ap-south-1')
        ec2.create_instances(
            ImageId="ami-0da59f1af71ea4ad2",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
        )
        print("<p>OS launched successfully.</p>")
    except Exception as e:
        print(f"<p>Failed to launch OS: {str(e)}</p>")

try:
    form = cgi.FieldStorage()
    image_file = form['image']

    if image_file.filename:
        # Read the image file into a memory buffer
        image_stream = io.BytesIO(image_file.file.read())
        image_array = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if img is None:
            print("<p>Failed to load image. Please ensure the image file is valid.</p>")
        else:
            print("<p>Image loaded successfully.</p>")

            # Initialize MediaPipe Hands module
            mp_hands = mp.solutions.hands
            mp_drawing = mp.solutions.drawing_utils
            hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

            # Convert the image to RGB for MediaPipe
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            # Draw hand landmarks on the image
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Count fingers up
                finger_count = 0
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks = hand_landmarks.landmark
                        if landmarks[mp_hands.HandLandmark.THUMB_TIP].y < landmarks[mp_hands.HandLandmark.THUMB_IP].y:
                            finger_count += 1
                        if landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_DIP].y:
                            finger_count += 1
                        if landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y:
                            finger_count += 1
                        if landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.RING_FINGER_DIP].y:
                            finger_count += 1
                        if landmarks[mp_hands.HandLandmark.PINKY_TIP].y < landmarks[mp_hands.HandLandmark.PINKY_DIP].y:
                            finger_count += 1

                print(f"<p>Detected fingers: {finger_count}</p>")

                # Perform actions based on the number of fingers detected
                if finger_count == 1:
                    print("<p>Opening YouTube...</p>")
                    # webbrowser.open("https://www.youtube.com")  # Uncomment for actual action
                elif finger_count == 2:
                    print("<p>Opening LinkedIn...</p>")
                    # webbrowser.open("https://www.linkedin.com")  # Uncomment for actual action
                elif finger_count == 3:
                    print("<p>Opening GitHub...</p>")
                    # webbrowser.open("https://github.com")  # Uncomment for actual action
                elif finger_count == 4:
                    print("<p>Launching OS...</p>")
                    launch_os()
                else:
                    print("<p>No specific action for this number of fingers.</p>")
            else:
                print("<p>No hand detected. Please try again with a clear hand image.</p>")

    else:
        print("<p>No image file received.</p>")

except Exception as e:
    print(f"<p>An error occurred: {str(e)}</p>")
