import os

from classes.player import Player

class CaptainedPlayer(Player):

    def __init__(self, id, name, photo_url, points, fpl_client, captainedBy):
        super().__init__(id, name, photo_url, points)
        self.fpl_client = fpl_client
        self.fixture = self.get_fixture(self.id)
        self.captainedBy = captainedBy
        # self.captainedByPercent = captainedByPercent #TODO

    def get_fixture(self, player_id):
        return self.fpl_client.get_player_fixture(player_id)

