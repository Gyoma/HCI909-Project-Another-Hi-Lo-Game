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

        cards = card_detector.buff_detect_cards()
        image, deb_image = card_detector.last_images()

        # print(cards)

        cv2.imshow("Card Detector", image)
        cv2.imshow("Debug", deb_image)

        # Poll the keyboard. If 'q' is pressed, exit the main loop.
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cam_quit = True

    del card_detector