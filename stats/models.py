from django.db import models

class Team(models.Model):
    team_id = models.IntegerField(primary_key=True)
    team_name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=15)
    logo = models.CharField(max_length=50)

    def __str__(self):
        return self.abbrev
    
class Game(models.Model):
    game_id = models.BigIntegerField(primary_key=True)
    game_date = models.DateField()
    start_time = models.CharField(max_length=50)
    venue = models.CharField(max_length=50)
    away_team_id = models.IntegerField(default=0)
    home_team_id = models.IntegerField(default=0)

    def home_team(self):
        return Team.objects.get(team_id=self.home_team_id)
    
    def away_team(self):
        return Team.objects.get(team_id=self.away_team_id)
    
    def __str__(self):
        return f"{self.game_date} - {self.away_team} @ {self.home_team}"