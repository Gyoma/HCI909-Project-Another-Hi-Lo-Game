from detector.CardDetector import CardDetector
from utils.singletonmeta import SingletonMeta
from cards.card import Card

import weakref
import threading
import time

DEFAULT_BUFFER_SIZE = 25


class ThreadSafeList:
    def __init__(self):
        self.lock = threading.Lock()
        self._data = weakref.WeakKeyDictionary()

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


class ObservableCardDetector(metaclass=SingletonMeta):
    def __init__(self, vidoe_src=0, buffer_size=DEFAULT_BUFFER_SIZE):
        self.card_detector = CardDetector(vidoe_src, buffer_size)
        self.observers = []
        self.current_cards = ThreadSafeList()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        self.stop_thread = False

    def __del__(self):
        self.stop()

    def run(self):
        while True:
            time.sleep(0.1)

            detectedCards = self.card_detector.detect_cards(draw_data=False)
            if self.current_cards.is_equal(detectedCards):
                continue

            self.current_cards.set_list(detectedCards)
            self.notify_observers()

            if self.stop_thread:
                break

    def add_observer(self, observer):
        self.observers.append(observer)
    
    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        cards = self.__convert_predicted_to_actual_cards(self.current_cards.get_list())

        for observer in self.observers:
            observer.update(cards)

    def get_cards(self):
        return self.__convert_predicted_to_actual_cards(self.current_cards.get_list())

    def set_parameters(self, vidoe_src, buffer_size=DEFAULT_BUFFER_SIZE):
        self.card_detector = None

        self.card_detector = CardDetector(vidoe_src, buffer_size)
        self.current_cards.set_list([])

    def stop(self):
        self.stop_thread = True
        self.thread.join()
        self.card_detector = None

    def __convert_predicted_to_actual_cards(self, predicted_cards):
        cards = []
        for card_predicted in predicted_cards:
            cards.append(Card(Card.Suit.from_str(card_predicted.best_suit_match),
                         Card.Rank.from_str(card_predicted.best_rank_match)))
        return cards
