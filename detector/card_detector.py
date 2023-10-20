# This file was taken and modified from the following repo:
# https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
# 
# The video explaining the idea:
# https://youtu.be/m-QPjO-2IkA?si=p7HiM9ZAj1IWQFdY
#
# Thank to the author. It gave us a great start.

# Import necessary packages
import cv2
import numpy as np
import os
import detector.cards_helper as cards_helper
import detector.video_stream as video_stream
import ultralytics as ul
from common import constants

# OpenCV window settings
IM_WIDTH = 1280
IM_HEIGHT = 720

current_folder = os.path.dirname(os.path.abspath(__file__))

# Define font to use if needed
font = cv2.FONT_HERSHEY_SIMPLEX

class CardDetector:
    """
    A class responsible for finding and identifying cards on an image obtained from a camera.\n
    It uses YOLOv8 model to identify cards.\n

    With this you can obtain either identified cards of the last image from a camera.\n

    For greater stability it supports card identification buffering. The idea is to store the last buffer_size\n
    identifications (array of constants.REQ_CARDS_NUM cards) and based on them (statistically) provide the user\n
    with the best prediction. 

    To get identified cards without buffering use detect_cards or buff_detect_cards otherwise.\n

    You can also obtain an image from a camera via calling last_images method
    """

    def __init__(self, video_src = 0, buffer_size = 25) -> None:
        model_path = os.path.join(current_folder, "model", "weights", "best_s_3.pt")
        
        # CNN model to identify playing cards
        self.card_model = ul.YOLO(model_path)

        self.image = None
        self.pre_proc_image = None
        self.buffer_size = buffer_size
        self.cards_history = []

        # Initialize camera object and video feed from the camera. The video stream is set up
        # as a seperate thread that constantly grabs frames from the camera feed.
        # See VideoStream.py for VideoStream class definition
        self.video_stream = video_stream.VideoStream((IM_WIDTH, IM_HEIGHT), video_src)

    def __del__(self):
        # Close all windows and close the PiCamera video stream.
        self.video_stream.stop()
        cv2.destroyAllWindows()

    def buff_detect_cards(self, draw_data = True):
        cards, frame_rate_calc = self._detect_cards_helper()


        # We need constants.REQ_CARDS_NUM cards, so drop the rest or populate it with dummies
        cards = cards[:constants.REQ_CARDS_NUM]
        
        cards = np.pad(cards, (0, constants.REQ_CARDS_NUM - len(cards)), 
                       mode='constant', 
                       constant_values=(0, 0))

        self.cards_history.append(cards)

        # Draw latest contours
        if draw_data:
            image, _ = self.last_images()

            for card in cards:
                if card == 0:
                    continue

                cv2.drawContours(self.image, [card.contour], -1, (255, 0, 0), 2)

        # If required buff size is not reached
        if len(self.cards_history) != self.buffer_size:
            return []
        
        card_dicts = [{} for i in range(constants.REQ_CARDS_NUM)]

        # Calculate the most number of matches for each position
        for cards in self.cards_history:
            for i, card in enumerate(cards):
                if card == 0:
                    new_val = 1
                    
                    if card in card_dicts[i]:
                        new_val = card_dicts[i][card][1] + 1

                    card_dicts[i][card] = [0, new_val]
                    continue

                card_name = card.best_suit_match + card.best_rank_match
                
                new_val = 1
                if card_name in card_dicts[i]:
                    new_val = card_dicts[i][card_name][1] + 1

                card_dicts[i][card_name] = [card, new_val]

        cards = []

        # Pick the most frequent ones
        for card_dict in card_dicts:
            if len(card_dict) == 0:
                cards.append(0)
                continue

            card = sorted(card_dict.items(), key=lambda item : item[1][1], reverse=True)[0][1][0]

            cards.append(card)

        self.cards_history.pop(0)

        if not draw_data:
            return cards

        image, _ = self.last_images()

        for card in cards:
            if card == 0:
                continue

            # cv2.drawContours(self.image, [card.contour], -1, (255, 0, 0), 2)
            cards_helper.draw_results(image, card)
            
            # Draw framerate in the corner of the image. Framerate is calculated at the end of the main loop,
            # so the first time this runs, framerate will be shown as 0.
            cv2.putText(self.image, "FPS: " + str(int(frame_rate_calc)),
                        (10, 26), font, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

        return cards

    def detect_cards(self, draw_data = True):
        cards, frame_rate_calc = self._detect_cards_helper()

        if not draw_data:
            return cards

        image, _ = self.last_images()

        for card in cards:
            cv2.drawContours(self.image, [card.contour], -1, (255, 0, 0), 2)
            cards_helper.draw_results(image, card)
            
            # Draw framerate in the corner of the image. Framerate is calculated at the end of the main loop,
            # so the first time this runs, framerate will be shown as 0.
            cv2.putText(self.image, "FPS: " + str(int(frame_rate_calc)),
                        (10, 26), font, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

        return cards

    def _detect_cards_helper(self):
        # Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
        freq = cv2.getTickFrequency()
        frame_rate_calc = 1
        
        # Grab frame from the video stream
        self.image = self.video_stream.read()

        # If image is not valid then return
        if self.image.ndim == 0:
            return [], frame_rate_calc

        # Start timer (for calculating frame rate)
        t1 = cv2.getTickCount()

        # Pre-process camera image (gray, blur, and threshold it)
        self.pre_proc_image = cards_helper.preprocess_image(self.image)

        # Find and sort the contours of all possible cards in the image (query cards)
        cnts_sort = cards_helper.find_possible_cards(self.pre_proc_image)

        # Sort contours by x (from left ro right)
        if len(cnts_sort) > 0:
            bounding_boxes = [cv2.boundingRect(c) for c in cnts_sort]
            (cnts_sort, _) = zip(*sorted(zip(cnts_sort, bounding_boxes), key=lambda b: b[1][0]))

        # Initialize a new "cards" list to assign the card objects.
        # k indexes the newly made array of cards.
        cards = []

        # If there are no contours, do nothing
        if len(cnts_sort) != 0:

            # For each contour detected:
            for cnt in cnts_sort:

                # Create a card object from the contour and append it to the list of cards.
                # preprocess_card function takes the card image and model and
                # determines the cards properties (corner points, etc). It generates a
                # flattened constants.CARD_WIDTH x constants.CARD_HEIGHT image of the card, and isolates the card's
                # top left corner and identify it using the model afterwards.
                card = cards_helper.process_card(cnt, self.image, self.card_model)

                # Draw center point and match result on the image.
                if card.is_valid:
                    cards.append(card)

        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1. / time1

        return cards, frame_rate_calc

    def last_images(self):
        return self.image, self.pre_proc_image
