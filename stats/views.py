from django.shortcuts import render
from stats.utils.api_client import get_standings, get_team_roster, get_player_stats
import asyncio

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