from classes.captainedPlayer import CaptainedPlayer
from classes.fpl_api import FPLClient
from classes.contestant import Contestant
from classes.player import Player
import json
import boto3

client = boto3.client('ssm')

def getTransfers(event, context):
    league_id = 1267504

    # Setup the API client
    fpl_client = FPLClient()

    # 1. Get GW Number and populate Players list from FPL
    all_players = {}
    gw_number = fpl_client.current_gameweek_number
    player_data_json = fpl_client.get_all_players_data()

    # TODO: this is creating a player object for EVERY player in the game. might not be necessary
    for player in player_data_json:
        all_players[player["id"]] = Player(player["id"], player["web_name"], player["photo"], player["event_points"])

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
                    'has_2_free_transfers': calculate_if_contestant_had_an_extra_transfer(gw_number, contestant_transfers_history),
                    'moves': this_weeks_transfers,
                    # The total cost of the transfers made after free transfers are taken into account
                    'totalTransferCost': fpl_client.get_contestant_total_transfer_cost(contestant_id, gw_number)
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
        'mvp': contestants[0],
        # TODO: rename key
        'shitebag': contestants[-1],
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(week_info, default=lambda o: o.__dict__, indent=4)
    }

    return response

def getDifferentials(event, context):
    fpl_client = FPLClient()
    respBody = {
        "picks": fpl_client.get_high_scoring_picks_owned_by_contestants()
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(respBody, default=lambda o: o.__dict__, indent=4)
    }

    return response

def getCaptains(event, context):
    fpl_client = FPLClient()
    league_contestants = fpl_client.league_contestants
    gw_number = fpl_client.current_gameweek_number
    player_data = fpl_client.get_all_players_data()
    
    gameweek_captains = []
    gameweek_captain_objects = []
    test = []

    for contestant in league_contestants:
        captain_id = fpl_client.get_gameweek_captain_id(contestant.id, gw_number)
        captain_ids = map(lambda x: x['captainId'], gameweek_captains)

        test.append({
            "contestant": contestant.name,
            "captainId": fpl_client.get_gameweek_captain_id(contestant.id, gw_number),
            "gameweek_number": gw_number
        })

        if captain_id not in captain_ids:
            # Add the the new captain
            gameweek_captains.append({
                "captainId": captain_id,
                "captainedByContestants": [
                    {
                        "id": contestant.id,
                        "name": contestant.name
                    }
                ]
            })
        else:
            # Captain exists so add to its captainedBy array
            # Get the captain object from the array
            captain_entry = next((item for item in gameweek_captains if item['captainId'] == captain_id), None)
            captain_entry["captainedByContestants"].append(
                {
                    "id": contestant.id,
                    "name": contestant.name
                }
            )

    #  filter all player data to just captains
    for captain in gameweek_captains:
        #  filter all player data to just captains
        captain_obj = list(filter(lambda item: item['id'] == captain['captainId'], player_data))[0]
        gameweek_captain_objects.append(CaptainedPlayer(
            captain_obj["id"],
            captain_obj["web_name"],
            captain_obj["photo"],
            captain_obj["event_points"],
            fpl_client,
            captain["captainedByContestants"]
        ))

    response = {
        "statusCode": 200,
        "body": json.dumps(gameweek_captain_objects, default=lambda o: o.__dict__, indent=4)
    }

    return response
    

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
