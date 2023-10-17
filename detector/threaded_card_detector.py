from common.card import Card
from common import constants
from detector.card_detector import CardDetector
from detector.cards_helper import QueryCard

import weakref
import threading
import time
import copy

DEFAULT_BUFFER_SIZE = 25

# _card_detector = None

# def card_detector():
#     global _card_detector
    
#     if _card_detector is None:
#         _card_detector = ObservableCardDetector()
    
#     return _card_detector

# custom class wrapping a list in order to make it thread safe
class ThreadSafeList():
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
    def __init__(self, video_source_index = 2, buffer_size=DEFAULT_BUFFER_SIZE):
        self.video_source_index = video_source_index
        self.buffer_size = buffer_size
        self.current_cards = ThreadSafeList()
        
        self.run_thread = False
        self.thread = None

    def __del__(self):
        self.stop()

    def __run(self):
        while self.run_thread:
            time.sleep(0.1) # yeild

            predicted_cards = self.card_detector.buff_detect_cards(draw_data=False)
            cards = self.__convert_predicted_cards_to_game_cards(predicted_cards)
            self.current_cards.replace(cards)

            # self.notify_observers()

    # def add_observer(self, observer):
    #     self.observers.add(observer)
    
    # def remove_observer(self, observer):
    #     self.observers.remove(observer)

    # def notify_observers(self):
    #     cards = self.current_cards.snapshot()

    #     for observer in self.observers:
    #         observer.update(cards)

    def get_cards(self):
        return self.current_cards.snapshot()
    
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
