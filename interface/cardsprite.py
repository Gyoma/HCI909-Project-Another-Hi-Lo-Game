import os
import arcade

current_folder = os.path.dirname(os.path.abspath(__file__))

FACE_DOWN_IMAGE = os.path.join(current_folder, 'imgs', 'CARD-BACK.png')

class CardSprite(arcade.Sprite):
    """
    A class responsible for displaying a card on the screen.

    It's a wrapper around arcade.Sprite class with using card images from 'imgs' folder.
    """

    def __init__(self, card, is_face_up = False):
        self.card = card

        self.image_file_name = os.path.join(current_folder, 'imgs', f'{self.card.suit}-{self.card.rank}.png')

        super().__init__(FACE_DOWN_IMAGE, 1, hit_box_algorithm="None")

        if (is_face_up):
            self.face_up()
        else:
            self.face_down()

    def face_down(self):
        """ Turn card face-down """
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        """ Turn card face-up """
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    @property
    def is_face_down(self):
        """ Is this card face down? """
        return not self.is_face_up
    
    def get_texture(self):
        return self.texture
    
    @classmethod
    def card_sprite_size(cls):
        return arcade.load_texture(FACE_DOWN_IMAGE).width, arcade.load_texture(FACE_DOWN_IMAGE).height
