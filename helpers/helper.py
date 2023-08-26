class Helper:

  # Given a player datapoint, check if they scored above the given points threshold
  @staticmethod
  def scored_over_points_threshold(self, player, pointsThreshold):
      if player["event_points"] > 5:
          return True  

      return False