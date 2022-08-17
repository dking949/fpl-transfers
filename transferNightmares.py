from fpl_api import FPLClient
from contestant import Contestant
from player import Player
import json
import boto3
import click
import os

client = boto3.client('ssm')

def getTransfers(event, context):
    league_id = 1117937

    FPL_LOGIN = os.environ.get('FPL_LOGIN')
    FPL_PWD = os.environ.get('FPL_PWD')

    # 0. Login
    fpl_client = FPLClient(FPL_LOGIN, FPL_PWD)

    # 1. Get GW Number and populate Players list from FPL
    all_players = {}
    gw_number, player_data_json = fpl_client.get_all_players_data()

    for player in player_data_json:
        all_players[player["id"]] = Player(player["web_name"], player["photo"], player["event_points"])

    # 2. Get league details
    league_details = fpl_client.get_league_details(league_id)

    # 3. Create list of Contestants
    contestants = []
    for entry in league_details["standings"]["results"]:

        contestant_id = entry["entry"]
        contestant_transfers_history = fpl_client.get_contestants_transfers(contestant_id)

        if contestant_transfers_history:
            this_weeks_transfers = []
            for transfer in contestant_transfers_history:
                if transfer['event'] == gw_number:
                    this_weeks_transfers.append({
                        'in': all_players[transfer['element_in']],
                        'out': all_players[transfer['element_out']]
                    })

            if this_weeks_transfers:
                transfer_details = {
                    'has_free_transfer': calculate_if_contestant_had_a_free_transfer(gw_number, contestant_transfers_history),
                    'moves': this_weeks_transfers
                }

                contestant_chip_played = fpl_client.get_chip_played(contestant_id, gw_number)

                if contestant_chip_played not in Contestant.SAFE_CHIPS:
                    contestants.append(Contestant(contestant_id,
                                                  entry["player_name"],
                                                  entry["entry_name"],
                                                  transfer_details,
                                                  contestant_chip_played))

    contestants.sort(key=lambda x: x.points_delta, reverse=True)

    week_info = {
        'league_name': league_details["league"]["name"],
        'gw_number': gw_number,
        'mvp': contestants[0].toJSON(),
        'shitebag': contestants[-1].toJSON()
    }

    response = {
        "statusCode": 200,
        "body": week_info
    }

    return json.dumps(response)


def calculate_if_contestant_had_a_free_transfer(gw_number, contestant_transfers):
    free_transfer = False
    for gw in range(2, gw_number):
        count = 0
        for transfer in contestant_transfers:
            if transfer['event'] == gw:
                count = count + 1
        free_transfer = (count == 0) or (free_transfer and count < 2)
    return free_transfer
