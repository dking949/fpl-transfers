import requests
from helpers.helper import Helper

class FPLClient:

    def __init__(self):
        self.session = requests.Session()
        # Store the data from the api call on init as it is needed a lot
        self.all_data = self.session.get(self.fpl_bootstrap_static_url()).json()
        self.current_gameweek_number = self.get_current_gameweek_number()

    def fpl_root_url(self):
        return 'https://fantasy.premierleague.com/api'

    def fpl_bootstrap_static_url(self):
        return f'{self.fpl_root_url()}/bootstrap-static/'

    def fpl_contestant_url(self, contestant_id):
        return f'{self.fpl_root_url()}/entry/{contestant_id}'

    def fpl_contestant_transfers_url(self, contestant_id):
        return f'{self.fpl_contestant_url(contestant_id)}/transfers'

    def fpl_league_url(self, league_id):
        return f'{self.fpl_root_url()}/leagues-classic/{league_id}/standings/'

    # gets the current gameweek number
    def get_current_gameweek_number(self):
        gw_number = 0
        for event in self.all_data.get('events', []):
            if event.get('is_current'):
                gw_number = event.get("id")
                break

        return gw_number

    # TODO: rename badly named function
    def get_all_players_data(self):
        gw_number = 0
        for event in self.all_data.get('events', []):
            if event.get('is_current'):
                gw_number = event.get("id")
                break

        return gw_number, self.all_data.get("elements")

    def get_contestants_transfers(self, contestant_id):
        return self.session.get(self.fpl_contestant_transfers_url(contestant_id)).json()

    def get_chip_played(self, user_id, gw_num):
        url = f'{self.fpl_contestant_url(user_id)}/event/{gw_num}/picks/'
        return self.session.get(url).json().get("active_chip")

    def get_league_details(self, league_id):
        return self.session.get(self.fpl_league_url(league_id)).json()

    def get_contestant_total_transfer_cost(self, contestant_id, gameweek_number):
        url = f'{self.fpl_contestant_url(contestant_id)}/history/'
        contestant_info = self.session.get(url).json()
        return contestant_info.get("current")[gameweek_number - 1]["event_transfers_cost"]

    def get_gameweek_captain_id(self, contestant_id, gameweek_number):
        gameweek_picks = self.get_contestant_gameweek_picks(contestant_id, gameweek_number)
        captain = list(filter(lambda item: item['is_captain'] == True, gameweek_picks))[0]

        return captain['element']

    # Gets the given players current fixture in format team_name (H/A)
    # Eg: MUN (H), WHU (A)
    def get_player_fixture(self, player_id):
        url = f'{self.fpl_root_url()}/element-summary/{player_id}/'
        fixture = self.session.get(url).json().get("fixtures")[0]
        vs_team_id = ''
        is_home_fixture = fixture["is_home"]

        if (is_home_fixture):
            vs_team_id = fixture["team_a"]
        else:
            vs_team_id = fixture["team_h"]

        all_team_data = self.all_data.get("teams")
        vs_team_data = list(filter(lambda item: item['id'] == vs_team_id, all_team_data))[0]
        vs_team_short_name = vs_team_data["short_name"]

        if (is_home_fixture):
            return f'{vs_team_short_name} (H)'
        else:
            return f'{vs_team_short_name} (A)'

    def get_gameweek_high_scoring_players(self):
        raw_players_data = self.all_data.get("elements")
        lowerScoringThreshold = 5
        high_scoring_players = filter(lambda player: player.get("event_points", 0) > lowerScoringThreshold, raw_players_data)
        return list(high_scoring_players)
    
    # Get all picks for a contestant for a given gameweek
    def get_contestant_gameweek_picks(self, contestant_id, gameweek_number):
        url = f'{self.fpl_contestant_url(contestant_id)}/event/{gameweek_number}/picks/'
        # all players the contestant is using this week
        return self.session.get(url).json().get("picks")
    
    def get_league_id(self):
        clos_ard_league_id = 1267504
        return clos_ard_league_id
    
    def get_high_scoring_picks_owned_by_contestants(self):
        allPlayerPicks = []
        contestant_picks_dict = {}
        contestant_ids = self.get_league_contestant_ids(self.get_league_id())

        for id in contestant_ids:
            contestantPicks = self.get_contestant_gameweek_picks(id, self.current_gameweek_number)
            contestant_picks_dict[id] = contestantPicks
            
            # Add unique picks to allPlayerPicks list
            for pick in contestantPicks:
                if pick not in allPlayerPicks:
                    allPlayerPicks.append(pick)

        # Filter allPlayerPicks down to only include high scorers
        high_scoring_players = self.get_gameweek_high_scoring_players()
        owned_high_scoring_players = [scorer for scorer in high_scoring_players if scorer['id'] in {pick['element'] for pick in allPlayerPicks}]
        owned_high_scoring_players = list(map(self.trim_player_object , owned_high_scoring_players))
        
        # For each owned_high_scoring_players, find out who owns him. If a contestant owns him
        # their ID will be added to an ownedBy array in the player object
        for contestant_id, player_picks in contestant_picks_dict.items():
            for pick in player_picks:
                player_id = pick["element"]
                for player in owned_high_scoring_players:
                    if player_id == player["id"]:
                        if "ownedBy" not in player:
                            player["ownedBy"] = []
                        player["ownedBy"].append(contestant_id)

        return owned_high_scoring_players

    # For the given league, fetch all contestant ids
    def get_league_contestant_ids(self, league_id: int):
        league_standings = self.get_league_details(league_id)['standings']['results']
        contestant_ids = []
        for contestant in league_standings:
            contestant_ids.append(contestant['entry'])

        return contestant_ids

    def trim_player_object(self, player):
        return {
            "id": player["id"],
            "points": player["event_points"],
            "name": player["web_name"]
        }
    

    # Need to filter high scoring player list down to players contestants have