import requests
import time


steamID_64 = '76561197999595616'
#steamID3 = '[U:1:39329888]'
numberOfLogs = 1000

response = requests.get("http://logs.tf/api/v1/log?player=" + steamID_64 + "&limit=" + str(numberOfLogs) + "&offset=0")
logIDs = response.json()

min_length = 60*10



def calc_combat_eff(log_json):
    combat_eff_blue = []
    combat_eff_red = []

    for name, val in log_json['players'].items():
        isMedic = 0
        for specific_class_stats in val['class_stats']:
            if specific_class_stats['type'] == 'medic' and specific_class_stats['total_time'] > 0.9 * log_json['length']:
                isMedic = 1

        if isMedic == 0:
            team = val['team']
            dmg_done = val['dmg']
            dmg_taken = val['dt']
            heals_received = val['hr']
            if heals_received == 0:
                heals_received = 1

            combat_eff_calc = (dmg_done-dmg_taken) / heals_received
            if team == 'Blue':
                combat_eff_blue.append(combat_eff_calc)
            else:
                combat_eff_red.append(combat_eff_calc)


    if sum(combat_eff_red) > sum(combat_eff_blue):
        combat_eff_winner = 'Red'
    elif sum(combat_eff_blue) > sum(combat_eff_red):
        combat_eff_winner = 'Blue'

    return [combat_eff_winner, combat_eff_red, combat_eff_blue]


matchesProcessed = 0
correctPreds = 0
APIcalls = 1
draws = 0

for entry in logIDs['logs']:
    if APIcalls % 18 == 0:
        print("Waiting for 10 seconds.")
        time.sleep(10)
        print("Wait is over.")

    specificLogID = entry['id']
    specificLogResponse = requests.get("http://logs.tf/api/v1/log/" + str(specificLogID))
    specificLogJSON = specificLogResponse.json()
    APIcalls += 1
    if specificLogJSON['length'] > min_length and len(specificLogJSON['players']) == 12:
        red_score = specificLogJSON['teams']['Red']['score']
        blue_score = specificLogJSON['teams']['Blue']['score']
        if red_score == blue_score:
            match_winner = 'Draw'
            draws += 1
        elif red_score > blue_score:
            match_winner = 'Red'
        elif blue_score > red_score:
            match_winner = 'Blue'

        res = calc_combat_eff(specificLogJSON)
        if res[0] == match_winner:
            correctPreds += 1
        else:
            print(f"(LogID, match winner, c_eff_red, c_eff_blue) = ({specificLogID}, {match_winner}, {sum(res[1])}, {sum(res[2])})")

        matchesProcessed += 1


print(f"Matches: {matchesProcessed}\n"
      f"Correct predictions: {correctPreds}\n"
      f"Incorrect predictions: {matchesProcessed-correctPreds}\n"
      f"Amount of draws: {draws}\n"
      f"Fraction of incorrect predictions that are draws: {draws/(matchesProcessed-correctPreds)}\n"
      f"Success rate: {correctPreds/matchesProcessed}")

