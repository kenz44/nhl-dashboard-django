import pytest
import datetime
from stats.models import Game, Team
from django.db import IntegrityError

pytestmark = pytest.mark.django_db

#-----------
# FIXTURES
#-----------

@pytest.fixture
def edmonton_oilers():
    return Team.objects.create(
        team_id = 1,
        team_name = "Edmonton Oilers",
        abbrev = "EDM",
        logo = "oilers.png"
    )

@pytest.fixture
def calgary_flames():
    return Team.objects.create(
        team_id = 2,
        team_name = "Calgary Flames",
        abbrev = "CGY",
        logo = "flames.png"
    )

@pytest.fixture
def game1(edmonton_oilers, calgary_flames):
    return Game.objects.create(
        game_id = 1,
        game_date = datetime.date(2025, 9, 3),
        start_time = "00:00",
        venue = "Test Venue",
        away_team_id = edmonton_oilers.team_id,
        home_team_id = calgary_flames.team_id
    )

#-----------
# GAME
#-----------

def test_game_creation(game1, edmonton_oilers, calgary_flames):
    assert game1.game_id == 1
    assert game1.game_date == datetime.date(2025, 9, 3)
    assert game1.start_time == "00:00"
    assert game1.venue == "Test Venue"
    assert game1.away_team_id == edmonton_oilers.team_id
    assert game1.home_team_id == calgary_flames.team_id

def test_game_no_team_ids():
    game = Game.objects.create(
        game_id = 2,
        game_date = datetime.date(2025, 9, 3),
        start_time = "11:11",
        venue = "Test Venue 2"
    )

    assert game.game_id == 2
    assert game.game_date == datetime.date(2025, 9, 3)
    assert game.start_time == "11:11"
    assert game.venue == "Test Venue 2"
    assert game.away_team_id == 0
    assert game.home_team_id == 0

def test_game_duplicate(game1):
    """ Creating a game with duplicate primary key should fail. """
    with pytest.raises(IntegrityError):
        Game.objects.create(
            game_id = 1,
            game_date = datetime.date(2025, 9, 3),
            start_time = "00:00",
            venue = "Duplicate Game",
            away_team_id = 1,
            home_team_id = 2
        )

def test_home_team(game1, calgary_flames):
    """ Teams created should return the team's abbreviation. """
    assert game1.home_team() == calgary_flames

def test_away_team(game1, edmonton_oilers):
    """ Teams created should return the team's abbreviation. """
    assert game1.away_team() == edmonton_oilers

def test_team_return(game1):
    """ Teams created should return the team's abbreviation. """
    assert str(game1) == "2025-09-03 - EDM @ CGY"