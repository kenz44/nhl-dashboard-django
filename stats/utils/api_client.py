import requests
# httpx is what allows python to complete tasks async
import httpx
from datetime import datetime

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
            'record': f"{team['wins']}-{team['losses']}-{team['otLosses']}",
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
            'id': player['id'],
            'name': f"{get_value(player['lastName'])}, {get_value(player['firstName'])}"
        })

    return player_list

def get_player_info(player_id):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch stats for player {player_id}: {response.status_code}")
        return []

    data = response.json()

    try:        
        basics = {
            'id': data['playerId'],
            'full_name': f"{get_value(data.get('firstName', 'N/A'))} {get_value(data.get('lastName', ''))}",
            'headshot': data.get('headshot', None),
            'position': data.get('position', '-'),
            'current_team': get_value(data.get('fullTeamName', 'N/A'))
        }
    # remember, if here then one of the above stats cannot be found.
    except KeyError as e:
        print(f"Something went wrong for player {player_id}: {e}")
        basics = None

    return basics

async def get_player_stats(player_id, season='regularSeason'):
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
        reg_stats = data['featuredStats'][season]['subSeason']
        
        stats = {
            'id': data['playerId'],
            'full_name': f"{get_value(data.get('firstName', 'N/A'))} {get_value(data.get('lastName', ''))}",
            'headshot': data.get('headshot', None),
            'position': data.get('position', '-'),
            'current_team': get_value(data.get('fullTeamName', 'N/A')),
            'games_played': reg_stats.get('gamesPlayed', 0),
            'goals': reg_stats.get('goals', 0),
            'assists': reg_stats.get('assists', 0),
            'points': reg_stats.get('points', 0),
            'plus_minus': reg_stats.get('plusMinus', 0),
            'penalty_minutes': reg_stats.get('pim', 0),
            'power_play_goals': reg_stats.get('powerPlayGoals', 0),
            'power_play_points': reg_stats.get('powerPlayPoints', 0),
            'short_handed_goals': reg_stats.get('shorthandedGoals', 0),
            'shots': reg_stats.get('shots', 0),
            'shooting_pctg': reg_stats.get('shootingPctg', 0.0),
        }
    # remember, if here then one of the above stats cannot be found.
    except KeyError as e:
        print(f"Something went wrong for player {player_id}: {e}")
        stats = None

    return stats

def get_last_n_games_stats(player_id, season, game_type, n):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/game-log/{season}/{game_type}"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching standings: {response.status_code}")
        return []

    data = response.json()
    games = data.get('gameLog', [])

    if n == 0:
        n_games = games
    else:
        n_games = games[:n]

    toi_seconds = 0
    g = 0
    a = 0
    pts = 0
    s = 0
    ppg = []
    dates = []
    for game in n_games:
        g += game.get('goals', 0)
        a += game.get('assists', 0)
        pts += game.get('points', 0)
        s += game.get('shots', 0)

        ppg.append(game.get('points', 0))
        dates.append(game.get('gameDate', 'XXXX-XX-XX'))

        game_toi = game.get('toi', '0:00')
        minutes, seconds = map(int, game_toi.split(':'))
        toi_seconds += (minutes * 60 + seconds)

    # put toi seconds into proper format
    avg_toi_seconds = toi_seconds / len(n_games)
    toi_minutes = int(avg_toi_seconds // 60)
    toi_remaining_s = int(avg_toi_seconds % 60)
    toi = f"{toi_minutes}:{toi_remaining_s:02d}"

    s_pctg = (g / s) *100

    stats = {
        'id': player_id,
        'games_played': len(n_games),
        'toi': toi,
        'goals': g,
        'assists': a,
        'points': pts,
        'shots': s,
        'shooting_pctg': s_pctg,
        'points_in_games': ppg,
        'dates': dates
    }
    print(stats)
    return stats

async def get_goalie_stats(goalie_id):
    url = f"https://api-web.nhle.com/v1/player/{goalie_id}/landing"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch stats for player {goalie_id}: {response.status_code}")
        return []

    data = response.json()

    try:
        # filter out prospects that are on rosters but have not played
        if 'featuredStats' not in data:
            print(f"Skipping {goalie_id} — no NHL stats available.")
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
            'reg_goals_against_avg': reg_stats.get('goalsAgainstAvg', 0),
            'reg_losses': reg_stats.get('losses', 0),
            'reg_ot_losses': reg_stats.get('otLosses', 0),
            'reg_save_pctg': reg_stats.get('savePctg', 0),
            'reg_shutouts': reg_stats.get('shutouts', 0),
            'reg_wins': reg_stats.get('wins', 0)
        }
    # remember, if here then one of the above stats cannot be found.
    except KeyError as e:
        print(f"Something went wrong for player {goalie_id}: {e}")
        stats = None

    return stats

def get_game_shots(game_id):
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to get game {game_id}: {response.status_code}")
        return []
    
    data = response.json()
    plays = data.get("plays", [])

    shot_types = {"blocked-shot", "shot-on-goal", "missed-shot", "goal"}
    shots = [play for play in plays if play.get("typeDescKey") in shot_types]
    
    away_team = data.get("awayTeam")
    home_team = data.get("homeTeam")
    
    away_team_shots = []
    home_team_shots = []

    for shot in shots:
        details = shot.get("details")
        if not details:
            continue
    
        team_id = details.get("eventOwnerTeamId")
        period = shot['periodDescriptor']['number']
        event_type = shot.get("typeDescKey")
        x = details.get("xCoord")
        y = details.get("yCoord")

        # have to switch both x,y in even periods
        # want to display all shots in one direction
        if period % 2 == 0:
            x = -x
            y = -y
        
        # if event_type != 'missed-shot':
        #     continue

        if team_id == away_team.get("id"):
            away_team_shots.append(((x, y), event_type))
        elif team_id == home_team.get("id"):
            home_team_shots.append(((x, y), event_type))
    
    return {
        "away_shots": away_team_shots,
        "home_shots": home_team_shots
    }

def get_date_games(date):
    url = f"https://api-web.nhle.com/v1/schedule/{date}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to get game data for {date}: {response.status_code}")
        return []
    
    data = response.json()
    gameWeek = data.get("gameWeek")

    game_data = []
    # for day in gameWeek:
    #     if day["date"] == date:
    #         games = day.get('games')
    #         for game in games:
    #             print(game.get("awayTeam"))
    #             game_data.append({
    #                 'id': game.get('id'),
    #                 'away_team': game.get('awayTeam'),
    #                 'home_team': game.get('homeTeam'),
    #             })
    for day in gameWeek:
        games = day.get('games')
        for game in games:
            game_data.append({
                'id': game.get('id'),
                'date': day.get('date'),
                'start_time': datetime.strptime(game['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ").time(),
                'venue': get_value(game['venue']),
                'away_team': game.get('awayTeam'),
                'home_team': game.get('homeTeam'),
            })

    return game_data