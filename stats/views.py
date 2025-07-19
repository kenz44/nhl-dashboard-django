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

async def team_roster_stats(request):
    standings = get_standings()
    team_abbrevs = sorted([team['team_abbr'] for team in standings])

    selected_team = request.GET.get('selected_team_abbr')
    players = []

    if selected_team:
        roster = await get_team_roster(selected_team)

        stats_task = [get_player_stats(player['id']) for player in roster]
        all_player_stats = await asyncio.gather(*stats_task)

        filtered_players = [p for p in all_player_stats if p is not None]
        players = sorted(filtered_players, key=lambda p: p['full_name'].split()[-1].lower())

    return render(request, 'roster_stats.html', {
        'players': players,
        'team_abbrevs': team_abbrevs,
        'selected_team': selected_team})