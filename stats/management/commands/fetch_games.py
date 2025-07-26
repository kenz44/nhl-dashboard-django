from django.core.management.base import BaseCommand
from datetime import datetime, timedelta

from stats.models import Game, Team
from stats.utils.api_client import get_date_games, get_value

class Command(BaseCommand):
    help = 'Fetch NHL 2024-2025 game schedule'

    def handle(self, *args, **kwargs):
        start_date = "2024-10-01"
        end_date = "2025-06-30"
        current_date = start_date

        while current_date <= end_date:
            week_games = get_date_games(current_date)

            for game in week_games:
                away_team = game['away_team']
                home_team = game['home_team']

                Game.objects.update_or_create(
                    game_id = game.get('id'),
                    defaults={
                        'game_date': game.get('date'),
                        'start_time': game.get('start_time'),
                        'venue': game.get('venue'),
                        'away_team_id': away_team['id'],
                        'home_team_id': home_team['id']
                    }
                )

                # get teams here so team_id matches across tables
                for team in [away_team, home_team]:
                    Team.objects.get_or_create(
                        team_id = team.get('id'),
                        defaults={
                            'team_name': get_value(team['commonName']),
                            'abbrev': team.get('abbrev'),
                            'logo': team.get('logo')
                        }
                    )

            current_date = (datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")