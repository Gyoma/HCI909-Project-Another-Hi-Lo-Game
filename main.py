import cv2
from detector.CardDetector import CardDetector

if __name__ == "__main__":
    ### ---- MAIN LOOP ---- ###
    # The main loop repeatedly grabs frames from the video stream
    # and processes them to find and identify playing cards.

    cam_quit = False  # Loop control variable
    card_detector = CardDetector(video_src=2)

    # Begin capturing frames
    while not cam_quit:

        card_detector.detect_cards()
        image, _ = card_detector.last_images()

        cv2.imshow("Card Detector", image)

        # Poll the keyboard. If 'q' is pressed, exit the main loop.
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cam_quit = True

    del card_detector