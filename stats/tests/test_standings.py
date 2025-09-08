"""
Tests for NHL Dashboard get_standings.

Covers:
- creation, string return, field constraints, edge cases, api integration testing.
"""

import pytest
from django.urls import reverse
from stats.views import standings_by_division
from stats.utils.api_client import get_standings

pytestmark = pytest.mark.django_db

#--------------------
# API STANDING CALLS
#--------------------

@pytest.mark.parametrize("status_code, data, expected_len", 
    [
        (200, {"standings": [{"teamName": "Edmonton Oilers",
                            "teamAbbrev": {"default": "EDM"},
                            "teamLogo": "oilers.png",
                            "divisionName": "Pacific",
                            "conferenceName": "Western",
                            "gamesPlayed": 10,
                            "wins": 6,
                            "losses": 3,
                            "otLosses": 1,
                            "points": 13,
                            "streakCode": "W",
                            "streakCount": 2,
                            "goalFor": 30,
                            "goalAgainst": 25,
                            "goalDifferential": 5,
                            "l10RegulationWins": 6,
                            "l10Losses": 3,
                            "l10OtLosses": 1,
                            "winPctg": 0.65,
                            "goalsForPctg": 3.0
                            }]}, 1),
        (500, {}, 0)
    ]
)
def test_get_standings(mocker, status_code, data, expected_len):
    """ Verify get_standings with and without data. """
    mock_response = mocker.Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = data

    print(data)

    # mocker before the https request ensures that the call is not live, but returns mock_response
    mocker.patch("stats.utils.api_client.requests.get", return_value = mock_response)
    standings = get_standings()

    assert isinstance(standings, list)
    assert len(standings) == expected_len

    # check all data fields when there is data
    if status_code == 200 and expected_len > 0:
        team = standings[0]
        print(team)

        assert team["team_name"] == "Edmonton Oilers"
        assert team["team_abbr"] == "EDM"
        assert team["logo"] == "oilers.png"
        assert team["division"] == "Pacific"
        assert team["conference"] == "Western"
        assert team["games_played"] == 10
        assert team["wins"] == 6
        assert team["losses"] == 3
        assert team["ot"] == 1
        assert team["record"] == "6-3-1"
        assert team["points"] == 13
        assert team["streak"] == "W2"
        assert team["gF"] == 30
        assert team["gA"] == 25
        assert team["diff"] == 5
        assert team["last10"] == "6-3-1"
        assert team["winPctg"] == 0.65
        assert team["gF_average"] == 3.0
        assert team["gA_average"] == 2.5

@pytest.mark.integration
def test_get_standings_integration():
    """ Verify NHL API call and check return values structure. """
    standings = get_standings()

    # returned data should be a non-empty list
    assert isinstance(standings, list)
    assert len(standings) > 0

    # team structure should be a dict
    team = standings[0]
    assert isinstance(team, dict)

    # check teamName exists and is a str
    assert "team_name" in team
    assert isinstance(team["team_name"], str)

    # check conference exists and is a str
    assert "conference" in team
    assert isinstance(team["conference"], str)

    # check points exists and is an int
    assert "points" in team
    assert isinstance(team["points"], int)

#--------------------
# STANDINGS VIEWS
#--------------------

@pytest.mark.parametrize("teams, expected_div_teams", 
    [
        (
            # teams
            [
                {"team": "Edmonton Oilers", "conference": "Western", "division": "Pacific"},
                {"team": "Florida Panthers", "conference": "Eastern", "division": "Atlantic"},
                {"team": "Carolina Hurricanes", "conference": "Eastern", "division": "Metropolitan"},
                {"team": "Winnipeg Jets", "conference": "Western", "division": "Central"},
                {"team": "Nashville Predators", "conference": "Eastern", "division": "Metropolitan"},
                {"team": "Toronto Maple Leafs", "conference": "Eastern", "division": "Atlantic"},
                {"team": "Calgary Flames", "conference": "Western", "division": "Pacific"},
                {"team": "Winnipeg Jets", "conference": "Western", "division": "Central"}
            ],

            # div_teams
            [
                {
                    "name": "Atlantic",
                    "teams": [
                        {"team": "Florida Panthers", "conference": "Eastern", "division": "Atlantic"},
                        {"team": "Toronto Maple Leafs", "conference": "Eastern", "division": "Atlantic"}
                    ]
                },
                {
                    "name": "Metropolitan",
                    "teams": [
                        {"team": "Carolina Hurricanes", "conference": "Eastern", "division": "Metropolitan"},
                        {"team": "Nashville Predators", "conference": "Eastern", "division": "Metropolitan"}
                    ]
                },
                {
                    "name": "Central",
                    "teams": [
                        {"team": "Winnipeg Jets", "conference": "Western", "division": "Central"},
                        {"team": "Winnipeg Jets", "conference": "Western", "division": "Central"}
                    ]
                },
                {
                    "name": "Pacific",
                    "teams": [
                        {"team": "Edmonton Oilers", "conference": "Western", "division": "Pacific"},
                        {"team": "Calgary Flames", "conference": "Western", "division": "Pacific"}
                    ]
                },
            ]
        ),
        # test for empty team list
        (
            [],
            [
                {"name": "Atlantic", "teams": []},
                {"name": "Metropolitan", "teams": []},
                {"name": "Central", "teams": []},
                {"name": "Pacific", "teams": []},
            ]
        )
    ]
)
def test_div_standings(teams, expected_div_teams):
    """ Verify division standings sorts as expected. """
    teams_by_div = standings_by_division(teams)
    assert teams_by_div == expected_div_teams

def test_standings_overview(client, mocker):
    """ Verify context response for view. """
    mock_standings = [
        {"team": "Edmonton Oilers", "conference": "Western", "division": "Pacific"},
        {"team": "Florida Panthers", "conference": "Eastern", "division": "Atlantic"},
        {"team": "Carolina Hurricanes", "conference": "Eastern", "division": "Metropolitan"},
        {"team": "Winnipeg Jets", "conference": "Western", "division": "Central"}
    ]

    mocker.patch("stats.views.get_standings", return_value = mock_standings)

    # reverse so we don't have to put the full url
    url = reverse("standings_overview")
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    assert "division_standings" in context
    assert "conference_standings" in context
    assert context["conference"] == "Western"

    # check all western teams
    western_teams = context["conference_standings"]
    assert all(team["conference"] == "Western" for team in western_teams)
    assert any(team["team"] == "Edmonton Oilers" for team in western_teams)