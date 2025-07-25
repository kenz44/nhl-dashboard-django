from django.shortcuts import render
from stats.utils.api_client import get_standings, get_team_roster, get_player_stats, get_game_shots, get_date_games
from hockey_rink import NHLRink
import matplotlib.pyplot as plt
import asyncio
import io
import base64
import mplcursors

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
    'EDM': '#041e42',
    'FLA': '#041e42',
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

async def team_roster_stats(request):
    standings = get_standings()
    team_abbrevs = sorted([team['team_abbr'] for team in standings])

    selected_team = request.GET.get('selected_team_abbr')
    if selected_team:
        team_data = next((team for team in standings if team['team_abbr'] == selected_team), None)
    else:
        team_data = None

    players = []
    team_color = "#fff"

    if selected_team:
        roster = await get_team_roster(selected_team)

        stats_task = [get_player_stats(player['id']) for player in roster]
        all_player_stats = await asyncio.gather(*stats_task)

        filtered_players = [p for p in all_player_stats if p is not None]
        players = sorted(filtered_players, key=lambda p: p['full_name'].split()[-1].lower())

        team_color = TEAM_COLORS.get(selected_team, "#fff")

    return render(request, 'roster_stats.html', {
        'players': players,
        'team_abbrevs': team_abbrevs,
        'selected_team': selected_team,
        'team_data': team_data,
        'team_color': team_color})

SHOT_SYMBOLS = {
    "blocked-shot": "s",
    "shot-on-goal": "o", 
    "missed-shot": "d", 
    "goal": "x"
}

def rink_plot(request):
    date = request.GET.get('selected_date')
    selected_game = request.GET.get('selected_game')

    date_games = get_date_games(date) if date else []

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

        plot_data = [('home', 'orange', shots['home_shots']),
                     ('away', 'black', shots['away_shots'])]
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
         'date_games': date_games})