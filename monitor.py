#!/usr/bin/env python
import cv2
from datetime import datetime
import time
import os
import logging
import subprocess
import sys
import socket


# Keep a log for debugging purposes.
logging.basicConfig(filename='home-monitor.log',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)


def upload_to_onedrive(filename):
    folder_name = filename.split('/')[1]

    # Create the date folder in OneDrive.
    try:
        subprocess.call(
            ['onedrive-cli', 'mkdir', 'home-monitor/{}'.format(folder_name)])
    except:
        pass

    # Upload the image.
    try:
        subprocess.call(
            ['onedrive-cli', 'put', filename,
             'home-monitor/{}'.format(folder_name)])
    except:
        pass

    # Upload the log.
    try:
        subprocess.call(
            ['onedrive-cli', 'put', 'home-monitor.log', 'home-monitor'])
    except:
        pass


def capture_camera():
    # Take pictures using OpenCV.
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Cannot open camera.")

    r, img = cap.read()
    cap.release()

    # Organize files by date.
    time_now = datetime.now()
    try:
        os.makedirs('archive/{:%Y-%m-%d}'.format(time_now))
    except:
        pass

    # Name the image by date and time.
    filename = 'archive/{:%Y-%m-%d}/{:%Y-%m-%d_%H%M%S}.jpg'.format(
        time_now, time_now)

    # Save the image locally and upload to OneDrive.
    cv2.imwrite(filename, img)
    logging.info('Capture saved to %s.' % filename)
    upload_to_onedrive(filename)
    logging.info('Capture uploaded.')

    # Remove the local file to save storage.
    os.remove(filename)
    logging.info('Local capture removed.')


if __name__ == '__main__':
    # Usage:
    #     python monitor.py [time-interval]
    #
    # time-interval: the interval in minutes for taking pictures.
    if len(sys.argv) == 1:
        # Take pictures every minute by default.
        minutes = 1.0
    else:
        minutes = float(sys.argv[1])
    time_interval = minutes * 60

    # Check Internet connection, we need to upload pictures to the cloud.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    logging.info('Started at {}'.format(s.getsockname()[0]))

    # Start taking pictures periodically.
    while True:
        capture_camera()
        time.sleep(time_interval)
    pass
