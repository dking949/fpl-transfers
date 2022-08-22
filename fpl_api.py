import requests

class FPLClient:

    def __init__(self, user, password):
        payload = {"login": user, "password": password,
                   "app": "plfpl-web", "redirect_uri": "https://fantasy.premierleague.com/"}

        self.session = requests.Session()
        # self.session.post("https://users.premierleague.com/accounts/login/", data=payload)

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
        jresp = self.session.get(self.fpl_bootstrap_static_url()).json()
        gw_number = 0
        for event in jresp.get('events', []):
            if event.get('is_current'):
                gw_number = event.get("id")
                break

        return gw_number, jresp.get("elements")

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
