import pytest
from stats.models import Team, Game
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

#-----------
# TEAM
#-----------

def test_team_creation(edmonton_oilers):
    team = edmonton_oilers

    # test all fields
    assert team.team_id == 1
    assert team.team_name == "Edmonton Oilers"
    assert team.abbrev == "EDM"
    assert team.logo == "oilers.png"

def test_team_return(edmonton_oilers):
    assert str(edmonton_oilers) == "EDM"

@pytest.mark.parametrize("abbrev", ["", "A", "AAAAAAAAAAAAAAAA", "!@#$%^&*()"])
def test_team_abbrev(abbrev):
    team = Team.objects.create(
            team_id = 2,
            team_name = "Test",
            abbrev = abbrev,
            logo = "test.png"
        )
    
    assert team.abbrev == abbrev

def test_logo_chars():
    long_logo = "a" *51

    team = Team.objects.create(
            team_id = 3,
            team_name = "Test",
            abbrev = "TES",
            logo = long_logo
        )

    with pytest.raises(Exception):
        team.full_clean()

def test_team_duplicate(edmonton_oilers):
    with pytest.raises(IntegrityError):
        Team.objects.create(
            team_id = 1,
            team_name = "Duplicate",
            abbrev = "DUP",
            logo = "duplicate.png"
        )