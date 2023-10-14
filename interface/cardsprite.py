import arcade

FACE_DOWN_IMAGE = ":resources:images/cards/cardBack_red2.png"

class CardSprite(arcade.Sprite):
    def __init__(self, card, is_face_up = False):
        self.card = card

        self.image_file_name = f":resources:images/cards/card{self.card.suit}{self.card.rank}.png"

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
