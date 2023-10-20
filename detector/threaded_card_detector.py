from common.card import Card
from common import constants
from detector.card_detector import CardDetector
from detector.cards_helper import QueryCard

import threading
import time
import copy

DEFAULT_BUFFER_SIZE = 25

class ThreadSafeList():
    """
    A custom class wrapping a list in order to make it thread safe
    """
    
    # constructor
    def __init__(self):
        # initialize the list
        self._list = list()
        # initialize the lock
        self._lock = threading.Lock()
 
    # add a value to the list
    def append(self, value):
        # acquire the lock
        with self._lock:
            # append the value
            self._list.append(value)
 
    # remove and return the last value from the list
    def pop(self):
        # acquire the lock
        with self._lock:
            # pop a value from the list
            return self._list.pop()
 
    # read a value from the list at an index
    def get(self, index):
        # acquire the lock
        with self._lock:
            # read a value at the index
            return self._list[index]
 
    def replace(self, data : list):
        # acquire the lock
        with self._lock:
            self._list = data

    def snapshot(self):
        # acquire the lock
        with self._lock:
            return copy.deepcopy(self._list)

    # return the number of items in the list
    def length(self):
        # acquire the lock
        with self._lock:
            return len(self._list)


class ThreadedCardDetector():
    """
    A class responsible for finding and identifying cards on an image obtained from a camera.\n
    It runs in its' own thread as daemon.\n

    With this class you can either obtain identified cards via get_cards or the last camera image.\n
    
    Basically, it's just a threaded wrapper for CardDetector, so check it first.
    """

    def __init__(self, video_source_index = 2, buffer_size=DEFAULT_BUFFER_SIZE):
        self.video_source_index = video_source_index
        self.buffer_size = buffer_size
        self.current_cards = ThreadSafeList()
        self.card_detector = None
        self.last_image = None
        
        self.run_thread = False
        self.thread = None

    def __del__(self):
        self.stop()

    def __run(self):
        while self.run_thread:
            time.sleep(0.1) # yeild

            predicted_cards = self.card_detector.buff_detect_cards(draw_data=False)
            self.last_image, _ = self.card_detector.last_images()
            
            cards = self.__convert_predicted_cards_to_game_cards(predicted_cards)
            self.current_cards.replace(cards)

    def get_cards(self):
        return self.current_cards.snapshot()
    
    def get_last_image(self):
        return copy.deepcopy(self.last_image) if self.last_image is not None else None
    
    def set_video_source(self, video_source_index):
        self.stop()

        self.video_source_index = video_source_index

        self.card_detector = CardDetector(video_source_index, self.buffer_size)
        self.current_cards.replace([])

        self.start()

    def set_buffer_size(self, buffer_size=DEFAULT_BUFFER_SIZE):
        self.stop()

        self.buffer_size = buffer_size

        self.card_detector = CardDetector(self.video_source_index, buffer_size)
        self.current_cards.replace([])

        self.start()

    def start(self):
        self.stop()
        self.card_detector = CardDetector(self.video_source_index, self.buffer_size)
        self.run_thread = True
        self.thread = threading.Thread(target=self.__run, daemon=True)
        self.thread.start()

    def stop(self):
        self.run_thread = False
        
        if self.thread is not None:
            self.thread.join()
        
        self.thread = None
        self.card_detector = None

    def __convert_predicted_cards_to_game_cards(self, predicted_cards):
        cards = []

        for predicted_card in predicted_cards:
            if not isinstance(predicted_card, QueryCard):
                continue

            cards.append(Card(Card.Suit[constants.CAPITALIZED_SUITS[predicted_card.best_suit_match]], 
                              Card.Rank[constants.CAPITALIZED_RANKS[predicted_card.best_rank_match]]))
            
        return cards
