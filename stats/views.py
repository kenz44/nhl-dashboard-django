from django.shortcuts import render
from stats.utils.api_client import get_standings, get_team_roster, get_stats, get_game_shots, get_last_n_games_stats, get_player_info
from hockey_rink import NHLRink
import matplotlib.pyplot as plt
import asyncio
import io
import base64

from stats.models import Game, Team
import json
from django.core.serializers.json import DjangoJSONEncoder
from asgiref.sync import sync_to_async

def standings_overview(request):
    standings = get_standings()

    division_standings = standings_by_division(standings)
    
    conference = request.GET.get('conference', 'Western')
    conference_standings = [team for team in standings if team['conference'] == conference]
    conferences = ['Western', 'Eastern']

    context = {
        'division_standings': division_standings,
        'conference_standings': conference_standings,
        'conference': conference,
        'conferences': conferences,
    }
    return render(request, 'standings_overview.html', context)

def standings_by_division(standings):
    divisions = {}
    for team in standings:
        divisions.setdefault(team['division'], []).append(team)

    division_list = []
    for division_name in ["Atlantic", "Metropolitan", "Central", "Pacific"]:
        division_list.append({
            "name": division_name,
            "teams": divisions.get(division_name, [])
        })
        
    return division_list

TEAM_COLORS = {
    'ANA': '#f47a38',
    'BOS': '#ffb81c',
    'BUF': '#003087',
    'CAR': '#cc0000',
    'CBJ': '#002654',
    'CGY': '#c8102e',
    'CHI': '#cf0a2c',
    'COL': '#6f263d',
    'DAL': '#006847',
    'DET': '#ce1126',
    'EDM': "#fda130",
    'FLA': "#D90505",
    'LAK': '#000000',
    'MIN': '#a6192e',
    'MTL': '#af1e2d',
    'NJD': '#ce1126',
    'NSH': '#ffb81c',
    'NYI': '#00539b',
    'NYR': '#0038a8',
    'OTT': '#e31837',
    'PHI': '#f74902',
    'PIT': '#fcB514',
    'SEA': '#005c5c',
    'SJS': '#006d75',
    'STL': '#004b87',
    'TBL': '#002868',
    'TOR': '#00205b',
    'UTA': '#00471b',
    'VAN': '#00205b',
    'VGK': '#b4975a',
    'WPG': '#041e42',
    'WSH': '#cf0a2c',
}

player_keys = {
    'games_played': 'gamesPlayed',
    'goals': 'goals',
    'assists': 'assists',
    'points': 'points',
    'plus_minus': 'plusMinus',
    'penalty_minutes': 'pim',
    'power_play_goals': 'powerPlayGoals',
    'power_play_points': 'powerPlayPoints',
    'short_handed_goals': 'shorthandedGoals',
    'shots': 'shots',
    'shooting_pctg': 'shootingPctg'
}

goalie_keys = {
    'season_games_played': 'gamesPlayed',
    'wins': 'wins',
    'losses': 'losses',
    'ot_losses': 'otLosses',
    'goals_against_avg': 'goalsAgainstAvg',
    'save_pctg': 'savePctg',
    'shutouts': 'shutouts'
}

async def team_roster_stats(request):
    standings = get_standings()
    team_abbrevs = sorted([team['team_abbr'] for team in standings])
    seasons = ['20252026', '20242025', '20232024', '20222023']

    selected_team = request.GET.get('selected_team_abbr')
    selected_season = request.GET.get('selected_season')
    if selected_team:
        team_data = next((team for team in standings if team['team_abbr'] == selected_team), None)
    else:
        team_data = None

    players = []
    goalies = []
    team_color = "#fff"

    if selected_team:
        roster = await get_team_roster(selected_team, selected_season)

        player_stats_task = [get_stats(player['id'], selected_season, player_keys) 
                      for player in roster
                      if player.get('positionCode', '') != 'G']
        goalie_stats_task = [get_stats(player['id'], selected_season, goalie_keys) 
                      for player in roster
                      if player.get('positionCode', '') == 'G']
        all_player_stats, all_goalie_stats = await asyncio.gather(
            asyncio.gather(*player_stats_task),
            asyncio.gather(*goalie_stats_task)    
        )

        filtered_players = [p for p in all_player_stats if p is not None]
        players = sorted(filtered_players, key=lambda p: p['full_name'].split()[-1].lower())

        filtered_goalies = [g for g in all_goalie_stats 
                            if g is not None and g.get('season_games_played', 0) > 0]
        goalies = sorted(filtered_goalies, key=lambda g: g['season_games_played'], reverse=True)
        print(f"goalies ----- {goalies}")

        team_color = TEAM_COLORS.get(selected_team, "#fff")

    return render(request, 'roster_stats.html', {
        'players': players,
        'goalies': goalies,
        'team_abbrevs': team_abbrevs,
        'seasons': seasons,
        'selected_team': selected_team,
        'selected_season': selected_season,
        'team_data': team_data,
        'team_color': team_color})

SHOT_SYMBOLS = {
    "blocked-shot": "s",
    "shot-on-goal": "o", 
    "missed-shot": "d", 
    "goal": "x"
}

def rink_plot(request):
    game_dates = Game.objects.values_list('game_date', flat=True).distinct()
    game_dates_list = [d.isoformat() for d in game_dates]
    game_dates_json = json.dumps(game_dates_list, cls=DjangoJSONEncoder)
    
    date = request.GET.get('selected_date')
    selected_game = request.GET.get('selected_game')

    date_games = []
    if date:
        date_games = Game.objects.filter(game_date=date)
        for game in date_games:
            game.home_team_abbrev = Team.objects.get(team_id=game.home_team_id).abbrev
            game.away_team_abbrev = Team.objects.get(team_id=game.away_team_id).abbrev

    if selected_game:
        shots = get_game_shots(selected_game)

        # create the fig and ax first
        fig, ax = plt.subplots(figsize=(30, 18))

        # put the rink on the ax next
        rink = NHLRink()
        rink.draw(ax=ax)

        # trying to get the markers on top
        for im in ax.get_images():
            im.set_zorder(1)

        # nhl rink width says -100 to 100
        ax.set_xlim(-100, 100)
        # nhl rink height says -42.5 to 42.5
        ax.set_ylim(-42.5, 42.5)
        ax.set_aspect('equal')

        plot_data = [('home', TEAM_COLORS.get(game.home_team_abbrev, "#fff"), shots['home_shots']),
                     ('away', TEAM_COLORS.get(game.away_team_abbrev, "#fff"), shots['away_shots'])]
        for team, color, team_shots in plot_data:
            for (x,y), shot_type in team_shots:
                marker = SHOT_SYMBOLS.get(shot_type, 'circle')
                size = 60 if shot_type == 'goal' else 25
                ax.scatter(x,y, color=color, marker=marker, s=size, label=shot_type, zorder=6)
                plt.text(x + 1, y + 1, f"({x},{y})", fontsize=8, color='gray')

        # save the fig to png for html usage
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
    
    else:
        image_base64 = None

    return render(request, 'rink_plot.html', 
        {'rink_image': image_base64,
         'selected_date': date,
         'selected_game': selected_game,
         'date_games': date_games,
         'game_dates': game_dates_json})

async def player_evaluation(request):
    standings = get_standings()
    team_abbrevs = sorted([team['team_abbr'] for team in standings])
    seasons = ["20252026", "20242025", "20232024", "20222023"]

    # get all params
    selected_team = request.GET.get('selected_team')
    selected_season = request.GET.get('selected_season')
    selected_player = request.GET.get('selected_player')
    selected_game_type = request.GET.get('selected_game_type')
    selected_time = request.GET.get('selected_time')

    team_data = next((team for team in standings if team['team_abbr'] == selected_team), None) if selected_team else None

    roster = []
    if selected_team and selected_season:
        roster = await get_team_roster(selected_team, selected_season)

    # set defaults
    if selected_player:
        if not selected_game_type:
            selected_game_type = '2'  # regularSeason 
        if not selected_time:
            selected_time = 'All Games'

    game_types = [
        {'name': 'Regular Season', 'label': 'regularSeason', 'id': 2},
        {'name': 'Playoffs', 'label': 'playoffs', 'id': 3}
    ]
    time_choices = ["All Games"] + [str(i) for i in range(1, 21)]

    player_info = {}
    player_stats = {}
    ppg = []
    dates = []

    if selected_player and selected_season and selected_game_type:
        # if functions re sync, wrap them
        player_info = await sync_to_async(get_player_info)(selected_player)
        n_games = 0 if selected_time == 'All Games' else int(selected_time)
        player_stats_data = await sync_to_async(get_last_n_games_stats)(selected_player, selected_season, selected_game_type, n_games)
        player_stats = player_stats_data
        ppg = player_stats.get('points_in_games', [])
        dates = player_stats.get('dates', [])

    return render(request, 'player_evaluation.html', {
        'team_abbrevs': team_abbrevs,
        'seasons': seasons,
        'selected_team': selected_team,
        'selected_season': selected_season,
        'team_data': team_data,
        'team_players': roster,
        'selected_player': selected_player,
        'selected_game_type': selected_game_type,
        'selected_time': selected_time,
        'game_types': game_types,
        'time_choices': time_choices,
        'player_info': player_info,
        'player_stats': player_stats,
        'ppg': json.dumps(ppg),
        'dates': json.dumps(dates)
    })