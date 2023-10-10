# Import necessary packages
import cv2
import numpy as np
import time
import os
import detector.Cards as Cards
import detector.VideoStream as VideoStream
import ultralytics as ul

# from models import model_wrapper
# from helper import constants, data_generator


### ---- INITIALIZATION ---- ###
# Define constants and initialize variables

# suits_source_folder = "./imgs/p_suits_i/"
# ranks_source_folder = "./imgs/p_ranks_i/"

# # data_generator.generate(suits_source_folder)
# # data_generator.generate(ranks_source_folder)

# suits_train_folder = os.path.join(suits_source_folder, "res")
# ranks_train_folder = os.path.join(ranks_source_folder, "res")

# modelRanks, modelSuits = model_wrapper.model_wrapper(constants.NUM_RANKS, data_path=ranks_train_folder, save_path='weights/rankWeights.h5'), \
#                          model_wrapper.model_wrapper(constants.NUM_SUITS, data_path=suits_train_folder, save_path='weights/suitWeights.h5'),

# data_generator.generate(card_source_folder)

# files = os.listdir("/home/artem/Downloads/px-conversions/")

# import shutil

# for file in files:

#     if (os.path.isdir("/home/artem/Downloads/px-conversions/" + file)):
#         continue

#     (rank, suit) = [*file.split(".")[0]][:2]

#     if rank == "T":
#         rank = "10"
#     elif rank == "J":
#         rank = "Jack"
#     elif rank == "Q":
#         rank = "Queen"
#     elif rank == "K":
#         rank = "King"

#     if suit == "C":
#         suit = "Clubs"
#     elif suit == "H":
#         suit = "Hearts"
#     elif suit == "D":
#         suit = "Diamonds"
#     elif suit == "S":
#         suit = "Spades"

#     file = os.path.join("/home/artem/Downloads/px-conversions/", file)

#     new_file = os.path.join(os.path.dirname(file), "res", rank + "-" + suit + ".jpg")

#     shutil.copy2(file, new_file)

#     print(rank, suit)


current_folder = os.path.dirname(os.path.abspath(__file__))

# for suit in ['hearts', 'clubs', 'spades', 'diamonds']:
#     for rank in ['ace', 'king', 'queen', 'jack', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
#         for ext in ['webp', 'png', 'jpg', 'jpeg']:
#             res = os.system(f'wget \"https://randomgenerate.io/_next/image?url=https%3A%2F%2Fstatic-abbreviations.nyc3.digitaloceanspaces.com%2Frandom-generate%2Frandom-card-generator%2F{suit}_{rank}.{ext}&w=384&q=75\" -O {os.path.join(path, "down", suit + "-" + rank + ".jpg")}')
            
#             print(suit, rank, ext, res)

#             if res == 0:
#                 break
    

# down_path = os.path.join(path, "down")
# file_names = os.listdir(down_path)
# for file_name in file_names:
#     img = cv2.imread(os.path.join(down_path, file_name))
    
#     if img is None:
#         continue
    
#     img = cv2.resize(img, (constants.CARD_WIDTH, constants.CARD_HEIGHT))

#     file_name_alone, file_ext = os.path.splitext(file_name)
#     file_suit, file_rank = file_name_alone.split('-')

#     cv2.imwrite(os.path.join(down_path, "res", file_rank.capitalize() + "-" + file_suit.capitalize() + file_ext), img)


# data_generator.crop_corners(os.path.join(path, "down"), os.path.join(path, "down", "res"), "-1")

# card_source_folder = "./imgs/card_data_1/"

# card_train_folder = os.path.join(card_source_folder, "res")

# card_model = model_wrapper.model_wrapper(constants.CARD_DENOMS_NUM, data_path=card_train_folder, wts_path='weights/weights.h5')

# train_single_card_folder = "/home/artem/projects/python/OpenCV-Playing-Card-Detector-master/imgs/single_cards_1/res/"

# for name in os.listdir(train_single_card_folder):
#     dir = os.path.join(train_single_card_folder, name)

#     if not os.path.isdir(dir):
#         continue
        
#     data_generator.generate(dir, dir)

# pure_data_path = os.path.join(path, "data", "pure_data")

# for name in os.listdir(pure_data_path):
#     dir = os.path.join(pure_data_path, name)

#     if not os.path.isdir(dir):
#         continue
        
#     data_generator.generate(dir, dir)

# data_generator.split_data_wrt_yolo("/home/artem/projects/python/OpenCV-Playing-Card-Detector-master/imgs/yolo_data/",
#                                    "/home/artem/projects/python/OpenCV-Playing-Card-Detector-master/imgs/yolo_train_data/")

from helper import constants

# Camera settings
IM_WIDTH = 1280
IM_HEIGHT = 720

# Define font to use
font = cv2.FONT_HERSHEY_SIMPLEX

class DetectedCard:
    def __init__(self) -> None:
        self.contour = []
        self.rank = "Unknown"
        self.suit = "Unknown"

class CardDetector:
    def __init__(self, video_src = 0, buffer_size = 10) -> None:
        model_path = os.path.join(current_folder, "model", "weights", "best_s_3.pt")
        self.card_model = ul.YOLO(model_path)

        self.image = None
        self.pre_proc_image = None
        self.buffer_size = buffer_size
        self.cards_history = []

        # Initialize camera object and video feed from the camera. The video stream is set up
        # as a seperate thread that constantly grabs frames from the camera feed.
        # See VideoStream.py for VideoStream class definition
        # IF USING USB CAMERA INSTEAD OF PICAMERA,
        # CHANGE THE THIRD ARGUMENT FROM 1 TO 2 IN THE FOLLOWING LINE:
        self.video_stream = VideoStream.VideoStream((IM_WIDTH, IM_HEIGHT), video_src).start()

    def __del__(self):
        # Close all windows and close the PiCamera video stream.
        cv2.destroyAllWindows()
        self.video_stream.stop()

    def detect_cards(self, draw_data = True):
        # Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
        freq = cv2.getTickFrequency()
        frame_rate_calc = 1
        
        # Grab frame from video stream
        self.image = self.video_stream.read()

        # Start timer (for calculating frame rate)
        t1 = cv2.getTickCount()

        # Pre-process camera image (gray, blur, and threshold it)
        self.pre_proc_image = Cards.preprocess_image(self.image)

        # Find and sort the contours of all possible cards in the image (query cards)
        cnts_sort = Cards.find_possible_cards(self.pre_proc_image)

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
                # preprocess_card function takes the card contour and contour and
                # determines the cards properties (corner points, etc). It generates a
                # flattened 200x300 image of the card, and isolates the card's
                # suit and rank from the image.
                card = Cards.process_card(cnt, self.image, self.card_model)

                # Draw center point and match result on the image.
                if card.is_valid:
                    cards.append(card)

                    if draw_data:
                        self.image = Cards.draw_results(self.image, card)

            # Draw card contours on image (have to do contours all at once or
            # they do not show up properly for some reason)
            if len(cards) != 0 and draw_data:
                cnts = [card.contour for card in cards]
                cv2.drawContours(self.image, cnts, -1, (255, 0, 0), 2)

        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1. / time1

        if draw_data:
            # Draw framerate in the corner of the image. Framerate is calculated at the end of the main loop,
            # so the first time this runs, framerate will be shown as 0.
            cv2.putText(self.image, "FPS: " + str(int(frame_rate_calc)),
                        (10, 26), font, 0.7, (255, 0, 0), 2, cv2.LINE_AA)


        return cards
    
    def last_images(self):
        return self.image, self.pre_proc_image
