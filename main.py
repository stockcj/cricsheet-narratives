'''
Convert cricsheet JSON to Narrative file
'''
import json
from datetime import datetime
from prettytable import PrettyTable
from match_data import MatchData, MatchInfo, MatchInningsOver, MatchInnings
from typing import Dict, List

def read_file(file_path: str) -> MatchData:
    with open(file_path) as file:
        data = json.load(file)

    # replace the 'from' key of any powerplays dicts with the name 'first_delivery'
    for innings in data['innings']:
        if 'powerplays' in innings:
            for powerplay in innings['powerplays']:
                powerplay['first_delivery'] = powerplay.pop('from')

    match_data = MatchData(**data)
    return match_data


def create_sub_heading(event: Dict) -> str:
    name = event['name']
    match_number = event.get('match_number', '')
    group = event.get('group', '')
    stage = event.get('stage', '')

    header_sub = f'{name}'

    if match_number:
        header_sub += f', match {match_number}.'

    if group:
        header_sub += f', Group: {group}'

    if stage:
        header_sub += f', Stage: {stage}'

    return header_sub


def create_header(match_info: MatchInfo) -> str:
    home_team: List = match_info['teams'][1]
    away_team: List = match_info['teams'][0]
    venue: MatchInfo.venue = match_info['venue']
    dates: MatchInfo.dates = match_info['dates']
    toss: MatchInfo.toss = match_info['toss']
    match_type: MatchInfo.match_type = match_info['match_type']
    officials: MatchInfo.officials = match_info.get('officials', None)
    event: MatchInfo.event = match_info.get('event', None)
    team_type: MatchInfo.team_type = match_info['team_type']
    players: MatchInfo.players = match_info['players']

    dates = [datetime.strptime(date, '%Y-%m-%d').strftime('%d %B %Y') for date in dates]

    header_title = f'{home_team.upper()} vs {away_team.upper()}'
    header_sub = create_sub_heading(event) if event else None
    
    header_description = f'{team_type.title()} {match_type} match between {home_team} and {away_team} at {venue} '

    if len(dates) > 1:
        header_description += f'between {dates[0]} and {dates[-1]}.'
    else:
        header_description += f'on {dates[0]}.'

    toss_string = f'{toss["winner"]} won the toss and decided to {toss["decision"]}.'
    
    teams = f'{home_team.upper()}\n{", ".join(players.get(home_team))}\n\n{away_team.upper()}\n{", ".join(players.get(away_team))}'

    header = header_title
    
    if header_sub:
        header += f'\n{header_sub}'
    
    header += f'\n\n{header_description}\n\n{toss_string}\n\n{teams}'
    
    if officials:
        header += f'\n\nUmpires: {", ".join(officials["umpires"])}\n\n'

    return header


def create_remark(runs: Dict, extras: Dict = None, wickets: List = None, replacements: Dict = None, review: Dict = None):
    total_runs = runs["total"]
    batter_runs = runs["batter"]
    non_boundary = runs.get('non_boundary')
    
    remark = ''

    if total_runs is 0 and wickets is None and replacements is None and review is None:
        remark = 'No incident or score'
    else:
        if replacements:
            role_replacements = replacements.get('role', [])
            match_replacements = replacements.get('match', [])
            for replacement in role_replacements:
                remark += f'{replacement["in"]} replaces {replacement["role"]} {replacement.get("out", "")}. {replacement["reason"].title()}.'
            for replacement in match_replacements:
                remark += f'{replacement["in"]} replaces {replacement["out"]}. {" ".join(word.capitalize() for word in replacement["reason"].split("_"))}.'

        if batter_runs > 0:
            if (batter_runs is 4 or batter_runs is 6) and non_boundary is None:
                remark += f'Batter hits, umpire signals Boundary {batter_runs}.'
            else:
                remark += f'Batter runs {batter_runs}'

        if extras:
            extras_string = ''
            for extra_type, extra_runs in extras.items():
                extras_string += f'{extra_runs} {extra_type}, '
            extras_string = extras_string.rstrip(', ')
            remark += f'Umpire signals {extras_string}.'

        if review:
            decision = review["decision"]
            if wickets:
                if decision is 'upheld':
                    remark += f'{review["by"]} successfully review.'
                else:
                    remark += f'{review["by"]} unsuccessfully review.'
            else:
                if decision is 'upheld':
                    remark += f'{review["batter"]} given out, but {review["by"]} successfully review.'
                else:
                    remark += f'{review["by"]} unsuccessfully review for dismissal.'

        if wickets:
            for wicket in wickets:
                method_of_dismissal = wicket["kind"]
                player_out = wicket["player_out"]
                fielders = wicket.get('fielders')
                if fielders:
                    fielders_string = ', '.join([f'{fielder["name"]} (sub)' if fielder.get("substitute") else fielder["name"] for fielder in fielders])
                    remark += f'{player_out} given out {method_of_dismissal} {fielders_string}.'
                else:
                    remark += f'{player_out} given out {method_of_dismissal}.'

    return remark.strip()    


def create_over(over: MatchInningsOver) -> Dict:
    over_num = over["over"] + 1
    deliveries = []
    for index, delivery in enumerate(over["deliveries"]):
        ball_num = index + 1
        bowler = delivery["bowler"]
        batter = delivery["batter"]
        runs = delivery["runs"]
        extras = delivery.get('extras')
        wickets = delivery.get('wickets')
        replacements = delivery.get('replacements')
        review = delivery.get('review')
        
        remarks = create_remark(runs, extras, wickets, replacements, review)

        ball = {"num": ball_num, "bowler": bowler, "batter": batter, "remarks": remarks}

        deliveries.append(ball)
    
    formatted_over = {"over": over_num, "deliveries": deliveries}

    return formatted_over


def create_innings(index: int, innings: MatchInnings, match_type: str):

    innings_title = f'{innings["team"]}'

    if match_type in ['Test','MDM']:
        if index == 0 or index == 1:
            innings_title += ' - 1st Innings\n'
        else:
            innings_title += ' - 2nd Innings\n'
    else:
        innings_title += ' Innings\n'

    innings_overs = []

    for over in innings["overs"]:
        innings_overs.append(create_over(over))

    table = PrettyTable(['Over', 'Bowler', 'Batter', 'Delivery', 'Remarks'])

    table.align['Bowler'] = 'l'
    table.align['Batter'] = 'l'
    table.align['Remarks'] = 'l'
    
    for over in innings_overs:
        previous_over = None
        previous_bowler = None
        previous_batter = None
        for index, delivery in enumerate(over["deliveries"]):
            current_over = over["over"]
            current_bowler = delivery["bowler"]
            current_batter = delivery["batter"]

            this_over = current_over if current_over != previous_over else ""
            bowler = current_bowler if current_bowler != previous_bowler else ""
            batter = current_batter if current_batter != previous_batter else ""
            if index == len(over["deliveries"]) - 1:
                table.add_row([this_over, bowler, batter, delivery["num"], delivery["remarks"]], divider=True)
            else:
                table.add_row([this_over, bowler, batter, delivery["num"], delivery["remarks"]])
            previous_bowler = current_bowler
            previous_batter = current_batter
            previous_over = current_over
    
    return {"title": innings_title, "overs_table": table}

    
def create_narrative(innings_data: MatchInnings, match_type: str) -> List:

    match_narrative = []
    
    for index, innings in enumerate(innings_data):
        match_narrative.append(create_innings(index, innings, match_type))

    return match_narrative


def generate_output(match_data: MatchData) -> None:

    header = create_header(match_data.info)
    narrative = create_narrative(match_data.innings, match_data.info["match_type"])
    
    output = ''

    output += header

    for innings in narrative:
        output += f'\n\n{innings["title"]}\n{innings["overs_table"]}\n\n'

    with open('narrative_outputs/outfile.txt', 'w') as file:
        file.write(str(output))




match_data = read_file('json_files/1270838.json')

generate_output(match_data)
    

