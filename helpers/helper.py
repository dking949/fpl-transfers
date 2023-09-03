class Helper:

    # Given a player datapoint, check if they scored above the given points threshold
    @staticmethod
    def scored_over_points_threshold(self, player, pointsThreshold):
        if player["event_points"] > 5:
          return True  

        return False
  
  # Checks if the contestant rolled a free transfer
    def calculate_if_contestant_had_an_extra_transfer(gw_number, contestant_transfers):
        free_transfer = False
        for gw in range(2, gw_number):
            count = 0
            for transfer in contestant_transfers:
                if transfer['event'] == gw:
                    count = count + 1
            free_transfer = (count == 0) or (free_transfer and count < 2)
        return free_transfer
    

    # The replace_contestant_ids_with_contestant_objects method takes in two parameters:
    # contestants and ownedBy. It replaces the contestant IDs in the ownedBy list with
    # the corresponding contestant objects from the contestants list.
    def replace_contestant_ids_with_contestant_objects(contestants, ownedBy):
        id_to_contestant = {contestant.id: contestant for contestant in contestants}
        replaced_objects = [id_to_contestant[id] for id in ownedBy]
        return replaced_objects