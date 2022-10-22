import requests

class FPLClient:

    def __init__(self):
        self.session = requests.Session()
        # Store the data from the api call on init as it is needed a lot
        self.all_data = self.session.get(self.fpl_bootstrap_static_url()).json()

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
        url = f'{self.fpl_contestant_url(contestant_id)}/event/{gameweek_number}/picks/'

        # all players the contestant is using this week
        gameweek_picks = self.session.get(url).json().get("picks")
        captain = list(filter(lambda item: item['is_captain'] == True, gameweek_picks))[0]

        return captain['element']

    # Gets the given players current fixture in format team_name (H/A)
    # Eg: MUN (H), WHU (A)
    def get_player_fixture(self, player_id):
        url = f'{self.fpl_root_url}/element-summary/{player_id}'
        fixtures = self.session.get(url).json().get("fixtures")
        fixture= fixtures[0]

        vs_team_id = ''
        is_home_fixture = fixture["is_home"]
        if(is_home_fixture):
            vs_team_id = fixture["team_a"]
        else:
            vs_team_id = fixture["team_h"]

        all_team_data = self.all_data.get("teams")
        vs_team_data = list(filter(lambda item: item['id'] == vs_team_id, all_team_data))
        vs_team_short_name = vs_team_data["short_name"]

        if (is_home_fixture):
            return f'{vs_team_short_name} (H)'
        else:
            return f'{vs_team_short_name} (A)'

 # {
    #     "playerId": 599,
    #     "playerName": "Haaland",
    #     "photoUrl": "",
    #     "fixture": "BOU(H)",
    #     "captainedBy": [
    #         {
    #             "id": "4",
    #             "name": "Darren"
    #         },
    #         {
    #             "id": "44",
    #             "name": "James"
    #         }
    #     ],
    #     "captainedByPercent": "60"
    # },