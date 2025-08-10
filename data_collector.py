from datetime import datetime, date
import json
import os
from src import api_client, model, probabilities, value_finder

HISTORY_FILE = "history.json"

def load_allowed_leagues():
    """Loads the list of allowed league IDs from the config file."""
    try:
        with open("config/leagues.json", "r") as f:
            leagues_data = json.load(f)
            return set(leagues_data.values())
    except FileNotFoundError:
        print("Warning: config/leagues.json not found. No league filter will be applied.")
        return None

def get_daily_fixtures():
    """Fetches all fixtures for the current day."""
    today = date.today().strftime('%Y-%m-%d')
    endpoint = "fixtures"
    params = {"date": today}

    print(f"Fetching fixtures for {today}...")
    response = api_client.make_api_request(endpoint, params)

    if not response or not response.get('response'):
        print("Could not fetch fixtures.")
        return []

    return response['response']

def run_analysis(existing_fixture_ids: set):
    """
    Runs the full analysis pipeline for new fixtures and returns the new bets.
    """
    if not api_client.API_KEY or api_client.API_KEY == 'VotreCléApiIci':
        print("ERROR: API key not found or not set. Exiting.")
        return None

    newly_found_bets = []
    allowed_league_ids = load_allowed_leagues()
    fixtures = get_daily_fixtures()

    if not fixtures:
        return []

    print(f"Found {len(fixtures)} total matches for today.")

    # Filter out fixtures that have already been analyzed
    new_fixtures = [f for f in fixtures if f['fixture']['id'] not in existing_fixture_ids]

    if allowed_league_ids:
        filtered_fixtures = [
            f for f in new_fixtures if f.get('league', {}).get('id') in allowed_league_ids
        ]
        print(f"Analyzing {len(filtered_fixtures)} new matches from your allowed list.")
    else:
        filtered_fixtures = new_fixtures
        print(f"Analyzing {len(filtered_fixtures)} new matches.")


    for fixture_data in filtered_fixtures:
        try:
            fixture_id = fixture_data['fixture']['id']
            home_team_name = fixture_data['teams']['home']['name']
            away_team_name = fixture_data['teams']['away']['name']
            league_name = fixture_data['league']['name']

            print(f"\nAnalyzing: {home_team_name} vs {away_team_name}")

            score_matrix, home_lambda, away_lambda = model.calculate_poisson_probabilities(
                fixture_data['teams']['home']['id'],
                fixture_data['teams']['away']['id'],
                fixture_data['league']['id'],
                fixture_data['league']['season']
            )
            if score_matrix is None: continue

            our_probs = probabilities.get_market_probabilities(score_matrix, home_lambda, away_lambda)
            if not our_probs: continue

            bookmaker_odds = value_finder.get_odds_for_fixture(fixture_id)
            if not bookmaker_odds: continue

            value_bets_found = value_finder.find_value_bets(our_probs, bookmaker_odds)

            if value_bets_found:
                print(f"--- Found {len(value_bets_found)} value bets ---")
                for bet in value_bets_found:
                    bet_details = {
                        "fixture_id": fixture_id,
                        "match": f"{home_team_name} vs {away_team_name}",
                        "league": league_name,
                        "market": bet['market'],
                        "bet_value": bet['value'],
                        "probability": bet['prob'],
                        "odds": bet['odds'],
                        "value": bet['prob'] * bet['odds'],
                        "timestamp": datetime.now().isoformat()
                    }
                    newly_found_bets.append(bet_details)
            else:
                print("No value bets found.")

        except (KeyError, TypeError) as e:
            print(f"Error processing fixture {fixture_data.get('fixture', {}).get('id', 'N/A')}. Missing data: {e}")

    return newly_found_bets


if __name__ == "__main__":
    print("Starting data collection...")

    # Load existing history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                historical_bets = json.load(f)
            except json.JSONDecodeError:
                historical_bets = []
    else:
        historical_bets = []

    # Get IDs of fixtures already in history to avoid re-analyzing
    existing_ids = {bet['fixture_id'] for bet in historical_bets}

    # Run analysis for new fixtures
    new_results = run_analysis(existing_ids)

    if new_results is not None:
        # Append new results to history and save
        updated_history = historical_bets + new_results
        with open(HISTORY_FILE, "w") as f:
            json.dump(updated_history, f, indent=4)
        print(f"\nData collection complete. Found {len(new_results)} new value bets.")
        print(f"History file '{HISTORY_FILE}' updated with a total of {len(updated_history)} bets.")
    else:
        print("\nData collection failed.")
