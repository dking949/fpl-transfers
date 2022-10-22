import os

class Player:

    def __init__(self, id, name, photo_id, points):
        self.id = id
        self.name = name
        self.photo_url = self._create_photo_url(photo_id)
        self.points = points

    @staticmethod
    def _create_photo_url(photo_id):
        pre, ext = os.path.splitext(photo_id)
        photo_png_file = pre + ".png"
        photo_url = "https://resources.premierleague.com/premierleague/photos/players/110x140/p" + photo_png_file
        return photo_url

    def __str__(self):
        return f'{self.name}: {self.points} points'

    def __repr__(self):
        return self.__str__()

