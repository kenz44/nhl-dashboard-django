import requests
# httpx is what allows python to complete tasks async
import httpx

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

async def get_team_roster(team_abbr):
    # TODO: have season be a dropdown
    url = f"https://api-web.nhle.com/v1/roster/{team_abbr}/20242025"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch roster for {team_abbr}: {response.status_code}")
        return []

    roster_data = response.json()
    players = roster_data.get('forwards', []) + roster_data.get('defensemen', []) # + roster_data.get('goalies', [])

    player_list = []
    for player in players:
        player_list.append({
            'id': player['id']
        })

    return player_list

async def get_player_stats(player_id, season=None):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch stats for player {player_id}: {response.status_code}")
        return []

    data = response.json()

    try:
        # filter out prospects that are on rosters but have not played
        if 'featuredStats' not in data:
            print(f"Skipping {player_id} — no NHL stats available.")
            return None
        
        # get regular season stats
        reg_stats = data['featuredStats']['regularSeason']['subSeason']
        
        stats = {
            'id': data['playerId'],
            'full_name': f"{get_value(data.get('firstName', 'N/A'))} {get_value(data.get('lastName', ''))}",
            'headshot': data.get('headshot', None),
            'position': data.get('position', '-'),
            'current_team': get_value(data.get('fullTeamName', 'N/A')),
            'reg_season_games_played': reg_stats.get('gamesPlayed', 0),
            'reg_goals': reg_stats.get('goals', 0),
            'reg_assists': reg_stats.get('assists', 0),
            'reg_points': reg_stats.get('points', 0),
            'reg_plus_minus': reg_stats.get('plusMinus', 0),
            'reg_penalty_minutes': reg_stats.get('pim', 0),
            'reg_power_play_goals': reg_stats.get('powerPlayGoals', 0),
            'reg_power_play_points': reg_stats.get('powerPlayPoints', 0),
            'reg_short_handed_goals': reg_stats.get('shorthandedGoals', 0),
            'reg_shots': reg_stats.get('shots', 0),
            'reg_shooting_pctg': reg_stats.get('shootingPctg', 0.0),
        }
    # remember, if here then one of the above stats cannot be found.
    except KeyError as e:
        print(f"Something went wrong for player {player_id}: {e}")
        stats = None

    return stats