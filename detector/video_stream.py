############## Camera video stream creator ###############
#
# See the following web pages for a full explanation of the source code:
# https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
# https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

# Import the necessary packages
from threading import Thread
import cv2
import numpy as np


class VideoStream:
    """Camera object"""
    def __init__(self, resolution=(640,480), src=0):

        # Initialize the USB camera and the camera image stream
        self.stream = cv2.VideoCapture(src)
        ret = self.stream.set(cv2.CAP_PROP_FRAME_WIDTH,resolution[0])
        ret = self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,resolution[1])

        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	    # Create a variable to control when the camera is stopped
        self.stopped = False
        self.thread = None
        self.start()

    def __del__(self):
        self.stop()

    def start(self):
        self.stop()
        
	    # Start the thread to read frames from the video stream
        self.stopped = False
        self.thread = Thread(target=self.__update, daemon=True)
        self.thread.start()

    def __update(self):

        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
		# Return the most recent frame
        return np.copy(self.frame)

    def stop(self):
		# Indicate that the camera and thread should be stopped
        self.stopped = True

        if self.thread is not None:
            self.thread.join()

        self.thread = None
