"""
Tests for NHL Dashboard Game model.

Covers:
- creation, string return, team returns, field constraints, invalid teams, edge cases
"""

import pytest
import datetime
from stats.models import Game, Team
from django.db import IntegrityError
from django.core.exceptions import ValidationError

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
    """ Verify game creation with correct fields/ """
    assert game1.game_id == 1
    assert game1.game_date == datetime.date(2025, 9, 3)
    assert game1.start_time == "00:00"
    assert game1.venue == "Test Venue"
    assert game1.away_team_id == edmonton_oilers.team_id
    assert game1.home_team_id == calgary_flames.team_id

def test_game_no_team_ids():
    """ Check away and home team defaults are set. """
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
    """ Games created should return the home team. """
    assert game1.home_team() == calgary_flames

def test_away_team(game1, edmonton_oilers):
    """ Games created should return the away team. """
    assert game1.away_team() == edmonton_oilers

def test_team_return(game1):
    """ Games created should return the game string (YYYY-MM-DD - home_abbrev @ away_abbrev). """
    assert str(game1) == "2025-09-03 - EDM @ CGY"

def test_startTime_chars():
    """ Check the start time max length constraint. """
    long_startTime = "s" * 51

    game = Game.objects.create(
            game_id = 3,
            game_date = datetime.date(2025, 9, 3),
            start_time = long_startTime,
            venue = "Long Start Time",
            away_team_id = 1,
            home_team_id = 2
        )

    with pytest.raises(Exception):
        game.full_clean()

def test_venue_chars():
    """ Check the venue max length constraint. """
    long_venue = "v" * 51

    game = Game.objects.create(
            game_id = 4,
            game_date = datetime.date(2025, 9, 3),
            start_time = "00:00",
            venue = long_venue,
            away_team_id = 1,
            home_team_id = 2
        )

    with pytest.raises(ValidationError):
        game.full_clean()

@pytest.mark.parametrize("home_id", [0, 1, -1])
def test_home_team_ids(home_id):
    """ Check that the home_team_id can store different values. """
    game = Game.objects.create(
            game_id = 5,
            game_date = datetime.date(2025, 9, 3),
            start_time = "00:00",
            venue = "long_venue",
            away_team_id = 2,
            home_team_id = home_id
        )
    assert game.home_team_id == home_id

@pytest.mark.parametrize("away_id", [0, 1, -1])
def test_away_team_ids(away_id):
    """ Check that the away_team_id can store different values. """
    game = Game.objects.create(
            game_id = 6,
            game_date = datetime.date(2025, 9, 3),
            start_time = "00:00",
            venue = "long_venue",
            away_team_id = away_id,
            home_team_id = 2
        )
    assert game.away_team_id == away_id

@pytest.mark.parametrize("team_id", [0, -1])
def test_home_team_invalid(edmonton_oilers, team_id):
    """ Check that a game cannot be created with an invalid away team. """
    game = Game.objects.create(
            game_id = 7,
            game_date = datetime.date(2025, 9, 3),
            start_time = "00:00",
            venue = "Test Venue",
            away_team_id = edmonton_oilers.team_id,
            home_team_id = team_id
        )
    
    with pytest.raises(Team.DoesNotExist):
        game.home_team()

@pytest.mark.parametrize("team_id", [0, -1])
def test_away_team_invalid(edmonton_oilers, team_id):
    """ Check that a game cannot be created with an invalid home team. """
    game = Game.objects.create(
            game_id = 7,
            game_date = datetime.date(2025, 9, 3),
            start_time = "00:00",
            venue = "Test Venue",
            away_team_id = team_id,
            home_team_id = edmonton_oilers.team_id
        )
    
    with pytest.raises(Team.DoesNotExist):
        game.away_team()