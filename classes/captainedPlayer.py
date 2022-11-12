import os

from classes.player import Player

class CaptainedPlayer(Player):

    def __init__(self, id, name, photo_url, points, fpl_client, captainedBy):
        super().__init__(id, name, photo_url, points)
        self.photo_url = photo_url
        self.fixture = self._get_fixture(fpl_client, id)
        self.captainedBy = captainedBy
        # self.captainedByPercent = captainedByPercent #TODO

    def _get_fixture(self, fpl_client, id):
        return fpl_client.get_player_fixture(id)

