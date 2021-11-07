
#!/usr/bin/env python
# this came from kite_ros basic motion detection as a structure for open cv imaged display but will now
# be stripped back to basics and see what it can do


# standard library imports
import numpy as np
import PySimpleGUI as sg
import time
import cv2
import argparse
import imutils
# kite_ros imports
from kite_logging import writelogs, writelogheader, writepictheader, closelogs


class Config(object):
    def __init__(self, source=2, kite='Standard', masklimit=10000,
                 logging=0, numcams=1, check_motor_sim=False, setup='Standard'):
        self.source = source
        self.kite = kite
        self.masklimit = masklimit
        self.logging = logging
        self.numcams = numcams
        self.check_motor_sim = check_motor_sim
        self.setup = setup
        self.writer = None

    @staticmethod
    def getlogheaders():
        return ('source', 'kite', 'masklimit', 'numcams', 'check_motor_sim', 'setup')

    def getlogdata(self):
        return (self.source, self.kite, self.masklimit, self.numcams, self.check_motor_sim, self.setup)



def display_stats():
    cv2.putText(frame, 'Test', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
    return


# MAIN ROUTINE START
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, default='cachedH.npy',
                    help='Filename to load cached matrix')
parser.add_argument('-l', '--load', type=str, default='yes',
                    help='Do we load cached matrix')
parser.add_argument('-k', '--kite', type=str, default='Standard',
                    help='Kite either Standard or Manual or Manbar')
parser.add_argument('-s', '--setup', type=str, default='Standard',
                    help='Standard, BarKiteActual, KiteBarInfer, KiteBarTarget')
# Standard means no connections between KiteAngle, KiteTargetAngle and Bar Angles others
# show connections from and to ie BarKiteActual the Kite angle is updated from the bar Angle
# This allows direct motor commands to be sent
parser.add_argument('-m', '--motortest', type=int, default=0, help='motortest either 0 or 1')
args = parser.parse_args()

# iphone
masklimit = 1000
# wind
# masklimit = 1000
# config = 'yellowballs'  # alternative when base not present will also possibly be combo
# KITETYPE = 'indoorkite'  # need to comment out for external
#KITETYPE = 'kite1'
KITETYPE = 'kite2'  # start for iphone SE video

# controls setup self.inputmodes = ('Standard', 'SetFlight', 'ManFly')
# setup options are Manfly, Standard

# initiate class instances
# config = Config(setup='Manfly', source=1, input='Joystick')
config = Config(source=2, kite=args.kite,  numcams=1, check_motor_sim=True, setup=args.setup, logging=1)

while config.source not in {1, 2}:
    config.source = input('Key 1 for camera or 2 for source')
# should define source here
if config.source == 1:
    camera = cv2.VideoCapture(-1)
    # probably need to go below route to do stitching but need to understand differences first
    config.logging = 1
else:
    # TODO at some point will change this to current directory and append file - not urgent
    # camera = cv2.VideoCapture(r'/home/donald/catkin_ws/src/kite_ros/scripts/choppedkite_horizshort.mp4')
    camera = cv2.VideoCapture(r'/home/ubuntu/catkin_ws/src/kite_ros/scripts/2020_test1.mp4')
    # Videostream seems to create errors with playback
    # camera = VideoStream(src=r'/home/donald/catkin_ws/src/kite_ros/scripts/choppedkite_horizshort.mp4').start()
    # camera =a VideoStream(src=r'/home/donald/catkin_ws/src/kite_ros/scripts/choppedkite_horizshort.mp4').start()
    # print('video:', camera.grab())
    config.logging = 1

# Initialisation steps
es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
kernel = np.ones((5, 5), np.uint8)
background = None
# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
counter = 0

sg.theme('Black')  # Pysimplegui setup

# below is proving clunky if we may start with any mode as the buttons names get fixed here - so if keeping this logic
# we must always create buttons with std setup and then cycle to correct mode
# create the window and show it without the plot
window = sg.Window('Kite ROS - Automated Flying', layout, no_titlebar=False, location=(50, 1000))
event, values = window.read(timeout=0)

writer = None
cv2.startWindowThread()
cv2.namedWindow('contours')
fps = 15
# fps = camera.get(cv2.CV_CAP_PROP_FPS)

time.sleep(2)
writelogheader(config)

# Main module loop START
while True:
    if config.source == 1:
        ret, frame = camera.stream.read()
    # change above for videostream from pyimagagesearch
    else:  # from file
        ret, frame = camera.read()
    # print('frame', frame.shape[1])
    height, width, channels = frame.shape
    writepictheader(config, height, width, fps)

    if background is None:
        background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        background = cv2.GaussianBlur(background, (21, 21), 0)
        continue

    display_stats()
    cv2.imshow("contours", frame)
    # below commented due to failing on 18.04
    # kiteimage.pubimage(imagemessage, frame)

    # read pysimplegui events
    event, values = window.read(timeout=0)
    quitkey = False
    if quitkey or event in ('Quit', None):  # quit if controls window closed or home key
        break

    counter += 1
    countertup = (counter,)
    writelogs(config)

# Exit and clean up
print("[INFO] cleaning up...")
closelogs(config)
cv2.destroyAllWindows()
camera.stop()


if writer is not None:
    writer.release()
