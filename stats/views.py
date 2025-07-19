from django.shortcuts import render
from collections import defaultdict
from stats.utils.api_client import get_standings

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
