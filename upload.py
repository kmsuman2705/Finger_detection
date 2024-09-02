#!/usr/bin/python3
import cgi
import os
import time
import cv2
import boto3
import webbrowser
from cvzone.HandTrackingModule import HandDetector

# Initialize AWS EC2 resource
ec2 = boto3.resource('ec2', region_name='ap-south-1')

# Define absolute path for the upload directory
upload_dir = "/var/www/cgi-bin/myupload/"

print("Content-Type: text/html")
print()

def launch_os():
    try:
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
        filename = "myimage.png"
        filepath = os.path.join(upload_dir, filename)

        # Save the uploaded file
        with open(filepath, 'wb') as f:
            f.write(image_file.file.read())
        print("<p>Image uploaded successfully.</p>")
    else:
        print("<p>No image file received.</p>")

except Exception as e:
    print(f"<p>An error occurred: {str(e)}</p>")

# Process the uploaded image
detector = HandDetector(maxHands=1, detectionCon=0.7)
img_path = os.path.join(upload_dir, "myimage.png")
img = cv2.imread(img_path)

if img is None:
    print("<p>Failed to load image. Please ensure the image file is valid.</p>")
else:
    print("<p>Image loaded successfully.</p>")
    hands, img = detector.findHands(img, draw=True)

    # Save the image with detected hands drawn (for debugging purposes)
    debug_image_path = os.path.join(upload_dir, "debug_image.png")
    cv2.imwrite(debug_image_path, img)

    if hands:
        for i, hand in enumerate(hands):
            lmlist = hand['lmList']
            print(f"<p>Hand {i+1} detected with landmarks: {lmlist}</p>")
            fingerup = detector.fingersUp(lmlist)
            finger_count = sum(fingerup)
            print(f"<p>Detected fingers for hand {i+1}: {fingerup}</p>")

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
