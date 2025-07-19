import requests

# if the obj is dict with 'default' key, return key, else return obj as string 
def get_value(obj):
    if isinstance(obj, dict) and 'default' in obj:
        return obj['default']
    return obj  

def get_standings():
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching standings: {response.status_code}")
        return []

    data = response.json()

    standings = []
    for team in data['standings']:
        team_data = {
            'team_name': get_value(team['teamName']),
            'team_abbr': get_value(team['teamAbbrev']['default']),
            'logo': get_value(team['teamLogo']),
            'division': get_value(team['divisionName']),
            'conference': get_value(team['conferenceName']),
            'games_played': team['gamesPlayed'],
            'wins': team['wins'],
            'losses': team['losses'],
            'ot': team['otLosses'],
            'points': team['points'],
            'streak': f"{team['streakCode']}{team['streakCount']}",
            'gF': team['goalFor'],
            'gA': team['goalAgainst'],
            'diff': team['goalDifferential'],
            'last10': f"{team['l10RegulationWins']}-{team['l10Losses']}-{team['l10OtLosses']}",
            'winPctg': team['winPctg'],
            "gF_average": team['goalsForPctg'],
            "gA_average": (team['goalAgainst'] / team['gamesPlayed'])
        }
        standings.append(team_data)

    return standings

def get_team_roster(team_abbr):
    url = f"https://api-web.nhle.com/v1/roster/{team_abbr}/current"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch roster for {team_abbr}: {response.status_code}")
        return []

    roster_data = response.json()
    players = roster_data.get('forwards', []) + roster_data.get('defensemen', []) + roster_data.get('goalies', [])

    player_list = []
    for player in players:
        position = player.get('positionCode', 'N/A')
        jersey = player.get('sweaterNumber', 'N/A')

        player_info = {
            'id': player['id'],
            'first_name': player['firstName']['default'],
            'last_name': player['lastName']['default'],
            'position': position,
            'jersey_number': jersey
        }
        player_list.append(player_info)

    return player_list