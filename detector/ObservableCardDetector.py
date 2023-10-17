from detector.CardDetector import CardDetector
from utils.singletonmeta import SingletonMeta
from cards.card import Card

import weakref
import threading
import time

DEFAULT_BUFFER_SIZE = 25


class ThreadSafePredictedCardsList:
    def __init__(self):
        self.lock = threading.Lock()
        self._data = []

    def set_list(self, new_list):
        with self.lock:
            self._data = new_list

    def get_list(self):
        with self.lock:
            return self._data

    def is_equal(self, other_list):
        with self.lock:
            if (len(self._data) != len(other_list)):
                return False

            for i in range(len(self._data)):
                if self._data[i].best_suit_match != other_list[i].best_suit_match or \
                    self._data[i].best_rank_match != other_list[i].best_rank_match:
                    return False
            return True


class ObservableCardDetector():
    def __init__(self, video_source_index=0, buffer_size=DEFAULT_BUFFER_SIZE):
        self.video_source_index = video_source_index
        self.buffer_size = buffer_size
        self.card_detector = CardDetector(self.video_source_index, self.buffer_size)
        self.observers = weakref.WeakSet()
        self.current_cards = ThreadSafePredictedCardsList()
        
        self.__launch_scan_thread()

    def __del__(self):
        self.stop()

    def run(self):
        while self.run_thread:
            time.sleep(0.1)

            cards_buffer = self.card_detector.detect_cards(draw_data=False)
            if self.current_cards.is_equal(cards_buffer):
                continue

            self.current_cards.set_list(cards_buffer)
            self.notify_observers()

    def add_observer(self, observer):
        self.observers.add(observer)
    
    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        cards = self.__convert_predicted_to_actual_cards(self.current_cards.get_list())

        for observer in self.observers:
            observer.update(cards)

    def get_cards(self):
        return self.__convert_predicted_to_actual_cards(self.current_cards.get_list())
    
    def set_video_source(self, video_source_index):
        self.stop()

        self.video_source_index = video_source_index

        self.card_detector = CardDetector(video_source_index, self.buffer_size)
        self.current_cards.set_list([])

        self.__launch_scan_thread()

    def set_buffer_size(self, buffer_size=DEFAULT_BUFFER_SIZE):
        self.stop()

        self.buffer_size = buffer_size

        self.card_detector = CardDetector(self.video_source_index, buffer_size)
        self.current_cards.set_list([])

        self.__launch_scan_thread()

    def stop(self):
        self.run_thread = False
        self.thread.join()
        self.card_detector = None

    def __convert_predicted_to_actual_cards(self, predicted_cards):
        cards = []
        for card_predicted in predicted_cards:
            cards.append(Card(Card.Suit.from_str(card_predicted.best_suit_match),
                         Card.Rank.from_str(card_predicted.best_rank_match)))
        return cards
    
    def __launch_scan_thread(self):
        self.run_thread = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
