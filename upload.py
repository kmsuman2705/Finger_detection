#!/usr/bin/python3
import cgi
import os
import time
import cv2
import webbrowser
import mediapipe as mp

# Define absolute path for the upload directory
upload_dir = "/var/www/cgi-bin/myupload/"

print("Content-Type: text/html")
print()

def launch_os():
    try:
        # Initialize AWS EC2 resource
        import boto3
        ec2 = boto3.resource('ec2', region_name='ap-south-1')
        instances = ec2.create_instances(
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
        timestamp = int(time.time())
        filename = f"myimage_{timestamp}.png"  # Use timestamp for uniqueness
        filepath = os.path.join(upload_dir, filename)

        # Save the uploaded file
        with open(filepath, 'wb') as f:
            f.write(image_file.file.read())
        print(f"<p>Image uploaded successfully: {filename}</p>")
    else:
        print("<p>No image file received.</p>")

except Exception as e:
    print(f"<p>An error occurred: {str(e)}</p>")

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Process the uploaded image
img_path = os.path.join(upload_dir, filename)
img = cv2.imread(img_path)

if img is None:
    print("<p>Failed to load image. Please ensure the image file is valid.</p>")
else:
    print("<p>Image loaded successfully.</p>")

    # Convert the image to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Draw hand landmarks on the image
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Save the image with detected hands drawn (for debugging purposes)
        debug_image_path = os.path.join(upload_dir, "debug_image.png")
        cv2.imwrite(debug_image_path, img)

        # Count fingers up
        finger_count = 0
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                # Example logic for counting fingers up
                # Adjust this logic based on your needs
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
