from classes.captainedPlayer import CaptainedPlayer
from classes.fpl_api import FPLClient
from classes.contestant import Contestant
from classes.player import Player
import json
import boto3

client = boto3.client('ssm')

def getTransfers(event, context):
    league_id = 1117937

    # Setup the API client
    fpl_client = FPLClient()

    # 1. Get GW Number and populate Players list from FPL
    all_players = {}
    gw_number, player_data_json = fpl_client.get_all_players_data()

    # TODO: this is creating a player object for EVERY player ij the game
    # might not be necessary
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
        'shitebag': contestants[-1],
        'captaincy': get_gameweek_captains(contestants, gw_number, all_players, fpl_client)
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(week_info, default=lambda o: o.__dict__, indent=4)
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

def get_gameweek_captains(contestants, gw_number, all_players, fpl_client):
    gameweek_captains = []

    def getId(entry):
        return entry.get("captainId")
    
    for contestant in contestants:
        captainId = fpl_client.get_gameweek_captain_id(contestant.id, gw_number)
        captainIds = map(getId, gameweek_captains)

        if captainId not in captainIds:
            gameweek_captains.append({
                "captainId": captainId,
                "captainedByContestants": [
                    {
                        "id": contestant.id,
                        "name": contestant.name
                    }
                ]
            })
        else:
            captainEntry = list(filter(lambda item: item['captainId'] == captainId, gameweek_captains))[0]
            captainEntry.get("captainedByContestants").append(
                {
                    "id": contestant.id,
                    "name": contestant.name
                }
            )

    gameweek_captain_objects = []

    for captain in gameweek_captains:
        captainId = captain["captainId"]
        player = all_players[captainId]
        captainedBy = captain.get("captainedByContestants")        
        # Create captained player class
        gameweek_captain_objects.append(
            CaptainedPlayer(
                getattr(player, "id"),
                getattr(player, "name"),
                getattr(player, "photo_url"),
                getattr(player, "points"),
                fpl_client,
                captainedBy)
        )

    return gameweek_captain_objects