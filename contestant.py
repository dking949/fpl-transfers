
class Contestant:

    SAFE_CHIPS = [
        'freehit',
        'wildcard'
    ]

    def __init__(self, user_id, name, team_name, transfer_details=None, chip_played=None):
        self.id = user_id
        self.name = name
        self.team_name = team_name

        self.transfer_details = transfer_details
        self.chip_played = chip_played

    @property
    def points_delta(self):
        # Calculate the points delta for transfers
        total_points_delta = 0
        if self.transfer_details:
            for move in self.transfer_details['moves']:
                move_delta = move['in'].points - move['out'].points
                total_points_delta += move_delta

            hit_cost = self.number_of_hits_taken * -4
            total_points_delta += hit_cost
        return total_points_delta

    @property
    def number_of_hits_taken(self):
        number_of_hits = 0
        if self.transfer_details:
            if self.chip_played not in self.SAFE_CHIPS:
                num_allowed_transfers = (2 if self.transfer_details['has_free_transfer'] else 1)

                number_of_hits = len(self.transfer_details['moves']) - num_allowed_transfers
        return number_of_hits

    def __str__(self):
        return f'{self.name}: {self.transfer_details}'

    def __repr__(self):
        return self.__str__()