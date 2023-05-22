"""
Convert cricsheet JSON to Narrative file.

This module provides functions to convert cricsheet JSON data into a narrative file format. It
includes functions for reading the JSON file, creating headers, generating remarks for each
delivery, formatting overs and innings, creating the match narrative, and generating the final
output.

Module functions:
- read_file: Reads the cricsheet JSON file and returns the MatchData object.
- create_sub_heading: Creates a sub-heading for the match header based on the event details.
- create_header: Creates the header for the match narrative.
- create_remark: Creates the remark for a delivery based on the runs, extras, wickets,
    replacements, and review data.
- create_over: Creates a formatted dictionary for an over.
- create_innings: Creates a formatted dictionary for an innings.
- create_narrative: Creates the narrative for the match.
- create_match_report: Generates the output narrative file.

Typing:
- MatchData: Represents the match data structure.
- MatchInfo: Represents the match information structure.
- MatchInningsOver: Represents the structure of an innings over.
- MatchInnings: Represents the structure of an innings.

Dependencies:
- json: Provides functions for working with JSON data.
- os: Provides functions for working with the operating system.
- helpers: A module that provides utility functions for string manipulation.
- datetime: Provides classes for manipulating dates and times.
- prettytable: A library for displaying tabular data in a visually appealing ASCII table format.

Note: This module assumes the availability of the required dependencies and the appropriate JSON
        file format conforming to cricsheet standards.
"""
import json
import os
from datetime import datetime
from typing import Dict, List

from prettytable import PrettyTable

from helpers import break_string
from match_data import MatchData, MatchInfo, MatchInnings, MatchInningsOver


def read_file(file_path: str) -> MatchData:
    """
    Reads the cricsheet JSON file and returns a MatchData object.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        MatchData: The parsed match data.

    """
    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)

    # replace the 'from' key of any powerplays dicts with the name 'first_delivery'
    for innings in data['innings']:
        if 'powerplays' in innings:
            for powerplay in innings['powerplays']:
                powerplay['first_delivery'] = powerplay.pop('from')

    data = MatchData(**data)
    return data


def create_sub_heading(event: Dict) -> str:
    """
    Creates a sub-heading for the match header.

    Args:
        event (Dict): The event data provided in the MatchData.

    Returns:
        str: The sub-heading string.

    """
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
    """
    Creates the match header.

    Args:
        match_info (MatchInfo): The match information.

    Returns:
        str: The header string.

    """
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

    header_description = f'\
        {team_type.title()} {match_type} match between {home_team} and {away_team} at {venue} '

    if len(dates) > 1:
        header_description += f'between {dates[0]} and {dates[-1]}.'
    else:
        header_description += f'on {dates[0]}.'

    header_description = break_string(header_description, 98)

    toss_string = f'{toss["winner"]} won the toss and decided to {toss["decision"]}.'

    home_players = break_string(", ".join(players.get(home_team)), 98, names=True)
    visiting_players = break_string(", ".join(players.get(away_team)), 98, names=True)

    teams = f'{home_team.upper()}\n{home_players}\n\n{away_team.upper()}\n{visiting_players}'

    header = header_title

    if header_sub:
        header += f'\n{header_sub}'

    header += f'\n\n{header_description}\n\n{toss_string}\n\n{teams}'

    if officials:
        header += f'\n\nUmpires: {", ".join(officials["umpires"])}\n\n'

    return header


def create_remark(
        runs: Dict,
        extras: Dict = None,
        wickets: List = None,
        replacements: Dict = None,
        review: Dict = None
        ) -> str:
    """
    Creates the remark for a particular ball delivery.

    Args:
        runs (Dict): The runs scored in the delivery.
        extras (Dict, optional): The extras in the delivery. Defaults to None.
        wickets (List, optional): The wickets taken in the delivery. Defaults to None.
        replacements (Dict, optional): The player replacements in the delivery. Defaults to None.
        review (Dict, optional): The review in the delivery. Defaults to None.

    Returns:
        str: The remark string.

    """
    total_runs = runs["total"]
    batter_runs = runs["batter"]
    non_boundary = runs.get('non_boundary')

    remark = ''

    if total_runs == 0 and wickets == None == replacements == None and review is None:
        remark = 'No incident or score.'
    else:
        if replacements:
            role_replacements = replacements.get('role', [])
            match_replacements = replacements.get('match', [])
            for replacement in role_replacements:
                remark += f'\
                    {replacement["in"]} replaces {replacement["role"]} {replacement.get("out", "")}.\
                        {replacement["reason"].title()}.'
            for replacement in match_replacements:
                remark += f'\
                    {replacement["in"]} replaces {replacement["out"]}.\
                        {" ".join(word.capitalize() for word in replacement["reason"].split("_"))}.'

        if batter_runs > 0:
            if (batter_runs in (4,6)) and non_boundary is None:
                remark += f'Batter hits, umpire signals Boundary {batter_runs}.'
            else:
                remark += f'Batter runs {batter_runs}. '

        if extras:
            extras_string = ''
            for extra_type, extra_runs in extras.items():
                if extra_runs == 1:
                    extra_type = extra_type.removesuffix('s')
                extras_string += f'{extra_runs} {extra_type}, '
            extras_string = extras_string.rstrip(', ')
            remark += f'Umpire signals {extras_string}.'

        if review:
            decision = review["decision"]
            if wickets:
                if decision == 'upheld':
                    remark += f'{review["by"]} successfully review.'
                else:
                    remark += f'{review["by"]} unsuccessfully review.'
            else:
                if decision == 'upheld':
                    remark += f'{review["batter"]}\
                        given out, but {review["by"]} successfully review.'
                else:
                    remark += f'{review["by"]} unsuccessfully review for dismissal.'

        if wickets:
            for wicket in wickets:
                method_of_dismissal = wicket["kind"]
                player_out = wicket["player_out"]
                fielders = wicket.get('fielders')
                if fielders:
                    fielders_string = ', '.join([f'{fielder["name"]} (sub)'
                                                 if fielder.get("substitute")
                                                 else fielder["name"] for fielder in fielders])
                    remark += f'{player_out} given out {method_of_dismissal} {fielders_string}.'
                else:
                    remark += f'{player_out} given out {method_of_dismissal}.'

    return remark.strip()


def create_over(over: MatchInningsOver) -> Dict:
    """
    Creates a formatted dictionary for an over.

    Args:
        over (MatchInningsOver): The over data.

    Returns:
        Dict: The formatted over data.

    """
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


def create_innings(index: int, innings: MatchInnings, match_type: str) -> Dict:
    """
    Creates a formatted dictionary for an innings.

    Args:
        index (int): The index of the innings.
        innings (MatchInnings): The innings data.
        match_type (str): The match type.

    Returns:
        Dict: The formatted innings data.

    """

    innings_title = f'{innings["team"]}'

    if match_type in ['Test','MDM']:
        if index in (0,1):
            innings_title += ' - 1st Innings\n'
        else:
            innings_title += ' - 2nd Innings\n'
    else:
        innings_title += ' Innings\n'

    innings_overs = []

    for over in innings["overs"]:
        innings_overs.append(create_over(over))

    table = PrettyTable(['Over', 'Bowler', 'Batter', 'Delivery', 'Remarks'])

    table._max_width = {'Over': 5, 'Bowler': 15, 'Batter': 15, 'Delivery': 8, 'Remarks': 45}
    table._min_width = {'Over': 5, 'Bowler': 15, 'Batter': 15, 'Delivery': 8, 'Remarks': 45}

    table.align['Bowler'] = 'l'
    table.align['Batter'] = 'l'
    table.align['Remarks'] = 'l'

    for over in innings_overs:
        previous_over = None
        previous_bowler = None
        previous_batter = None
        for i, delivery in enumerate(over["deliveries"]):
            current_over = over["over"]
            current_bowler = delivery["bowler"]
            current_batter = delivery["batter"]

            this_over = current_over if current_over != previous_over else ""
            bowler = current_bowler if current_bowler != previous_bowler else ""
            batter = current_batter if current_batter != previous_batter else ""
            if i == len(over["deliveries"]) - 1:
                table.add_row([this_over, bowler, batter, delivery["num"],
                               delivery["remarks"]], divider=True)
            else:
                table.add_row([this_over, bowler, batter, delivery["num"], delivery["remarks"]])
            previous_bowler = current_bowler
            previous_batter = current_batter
            previous_over = current_over

    return {"title": innings_title, "overs_table": table}


def create_narrative(innings_data: MatchInnings, match_type: str) -> List:
    """
    Creates the narrative for the match.

    Args:
        innings_data (MatchInnings): The innings data.
        match_type (str): The match type.

    Returns:
        List: The list of formatted innings data.

    """

    match_narrative = []

    for index, innings in enumerate(innings_data):
        match_narrative.append(create_innings(index, innings, match_type))

    return match_narrative


def create_match_report(data: MatchData) -> None:
    """
    Creates the match report.

    Args:
        match_data (MatchData): the MatchData representation of the cricsheet JSON data.

    """

    header = create_header(data.info)
    narrative = create_narrative(data.innings, data.info["match_type"])

    output = ''

    output += header

    for innings in narrative:
        output += f'\n\n{innings["title"]}\n{innings["overs_table"]}\n\n'

    filename = f'narrative_outputs/{data.info["dates"][0]}_{data.info["teams"][0].replace(" ", "_")}_vs_{data.info["teams"][1].replace(" ", "_")}.txt'

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(output))


def process_folder(cricsheet_folder_path: str) -> None:
    """
    Process each JSON file in the specified folder.

    Args:
        cricsheet_folder_path: A string representing the path to the folder containing JSON files.

    Returns:
        None
    """
    # Get a list of JSON files in the selected folder
    json_files = [file for file in os.listdir(cricsheet_folder_path) if file.endswith('.json')]

    for json_file in json_files:
        file_path = os.path.join(cricsheet_folder_path, json_file)
        match_data = read_file(file_path)
        create_match_report(match_data)


if __name__ == "__main__":
    # Prompt the user to select a folder
    folder_path = input('Enter the folder path for the folder containing cricsheet json files:')

    if folder_path:
        process_folder(folder_path)
