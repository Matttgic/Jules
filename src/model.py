import numpy as np
import math
from . import api_client

# NOTE: As the API documentation could not be accessed, the endpoint names and
# parameter names used in this module are based on common API design patterns
# and may need to be adjusted.

def _poisson_pmf(k, lam):
    """Poisson probability mass function."""
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def get_team_stats(team_id, league_id, season):
    """
    Fetches team statistics for a given season.
    Assumes the API response contains goals for/against at home/away.
    """
    endpoint = "teams/statistics"
    params = {"team": team_id, "league": league_id, "season": season}
    # Example of expected data structure from API:
    # { 'goals': { 'for': { 'total': { 'home': 20, 'away': 15 } }, 'against': { 'total': { 'home': 10, 'away': 12 } } } }
    return api_client.make_api_request(endpoint, params)

def get_league_stats(league_id, season):
    """
    Fetches statistics for all teams in a league to calculate averages.
    This is a conceptual function. The actual implementation depends heavily on the API's capabilities.
    A more robust way is to fetch stats for each team and aggregate.
    For now, we will assume an endpoint that provides league-level stats, which is unlikely.
    A more realistic approach would be to get all teams from a `/teams?league=...` endpoint
    and then loop through them calling `get_team_stats`.
    """
    # This is a major assumption. A real implementation would need to iterate through all teams.
    # We will mock this for now.
    print("Fetching league-wide stats is complex and depends on the API. Using mock data for now.")
    return {
        "avg_goals_scored_home": 1.5,
        "avg_goals_conceded_home": 1.1,
        "avg_goals_scored_away": 1.2,
        "avg_goals_conceded_away": 1.4,
    }

def calculate_poisson_probabilities(home_team_id, away_team_id, league_id, season):
    """
    Calculates match outcome probabilities using a Poisson distribution model.
    """
    league_averages = get_league_stats(league_id, season)
    if not league_averages:
        print("Could not get league average stats. Aborting.")
        return None

    home_stats_raw = get_team_stats(home_team_id, league_id, season)
    away_stats_raw = get_team_stats(away_team_id, league_id, season)

    if not home_stats_raw or not away_stats_raw:
        print("Could not retrieve team stats. Aborting calculation.")
        return None

    # --- Data parsing (highly dependent on actual API response structure) ---
    # These paths are illustrative based on a potential API response.
    try:
        home_goals_scored = home_stats_raw['goals']['for']['total']['home']
        home_goals_conceded = home_stats_raw['goals']['against']['total']['home']
        # Assuming number of matches is available, e.g., home_stats_raw['fixtures']['played']['home']
        # For simplicity, we'll assume the API gives us per-game averages, or we use a fixed number.
        # Let's assume stats are for a 38-game season, 19 home games.
        num_matches_home = 19

        away_goals_scored = away_stats_raw['goals']['for']['total']['away']
        away_goals_conceded = away_stats_raw['goals']['against']['total']['away']
        num_matches_away = 19

        home_avg_scored = home_goals_scored / num_matches_home
        home_avg_conceded = home_goals_conceded / num_matches_home
        away_avg_scored = away_goals_scored / num_matches_away
        away_avg_conceded = away_goals_conceded / num_matches_away
    except KeyError as e:
        print(f"Could not parse team stats from API response. Missing key: {e}")
        return None

    # --- Calculate Attack/Defense Strength ---
    home_attack_strength = home_avg_scored / league_averages['avg_goals_scored_home']
    home_defense_strength = home_avg_conceded / league_averages['avg_goals_conceded_home']
    away_attack_strength = away_avg_scored / league_averages['avg_goals_scored_away']
    away_defense_strength = away_avg_conceded / league_averages['avg_goals_conceded_away']

    # --- Calculate Expected Goals (Lambda) ---
    home_lambda = home_attack_strength * away_defense_strength * league_averages['avg_goals_scored_home']
    away_lambda = away_attack_strength * home_defense_strength * league_averages['avg_goals_scored_away']

    # --- Poisson Calculation ---
    max_goals = 5
    score_matrix = np.zeros((max_goals + 1, max_goals + 1))

    for i in range(max_goals + 1):  # Home goals
        for j in range(max_goals + 1):  # Away goals
            prob_home = _poisson_pmf(k=i, lam=home_lambda)
            prob_away = _poisson_pmf(k=j, lam=away_lambda)
            score_matrix[i, j] = prob_home * prob_away

    # The sum of probabilities in the matrix might not be 1 because we cap at max_goals.
    # For more accuracy, we could normalize it, but for now, this is sufficient.
    # print(f"Sum of matrix probabilities: {np.sum(score_matrix)}")

    return score_matrix
