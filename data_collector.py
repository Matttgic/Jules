import datetime
import json
from src import api_client, model, probabilities, value_finder

def load_allowed_leagues():
    """Loads the list of allowed league IDs from the config file."""
    try:
        with open("config/leagues.json", "r") as f:
            leagues_data = json.load(f)
            # We only need the IDs, so we extract the values.
            # Using a set for faster lookups.
            return set(leagues_data.values())
    except FileNotFoundError:
        print("Warning: config/leagues.json not found. No league filter will be applied.")
        return None
    except json.JSONDecodeError:
        print("Warning: Could not decode config/leagues.json. No league filter will be applied.")
        return None

def get_daily_fixtures():
    """
    Fetches all fixtures for the current day.
    """
    today = datetime.date.today().strftime('%Y-%m-%d')
    endpoint = "fixtures"
    params = {"date": today}

    print(f"Fetching fixtures for {today}...")
    response = api_client.make_api_request(endpoint, params)

    if not response or not response.get('response'):
        print("Could not fetch fixtures.")
        return []

    return response['response']

from sqlalchemy.orm import Session
from webapp import database
from webapp.database import Fixture, ValueBet

def analyze_and_store_fixture(db: Session, fixture_data: dict):
    """
    Runs the full analysis pipeline and stores the results in the database.
    """
    try:
        fixture_id = fixture_data['fixture']['id']

        # Check if the fixture has already been analyzed today
        existing_fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()
        if existing_fixture:
            # For simplicity, we assume if the fixture exists, it's analyzed for the day.
            # A more robust check might involve a timestamp comparison.
            print(f"Skipping fixture {fixture_id} (already in DB).")
            return

        league_id = fixture_data['league']['id']
        season = fixture_data['league']['season']
        home_team_id = fixture_data['teams']['home']['id']
        away_team_id = fixture_data['teams']['away']['id']
        home_team_name = fixture_data['teams']['home']['name']
        away_team_name = fixture_data['teams']['away']['name']
        league_name = fixture_data['league']['name']

        print(f"\nAnalyzing: {home_team_name} vs {away_team_name}")

        score_matrix = model.calculate_poisson_probabilities(home_team_id, away_team_id, league_id, season)
        if score_matrix is None: return

        our_probs = probabilities.get_market_probabilities(score_matrix)
        if not our_probs: return

        bookmaker_odds = value_finder.get_odds_for_fixture(fixture_id)
        if not bookmaker_odds: return

        value_bets_found = value_finder.find_value_bets(our_probs, bookmaker_odds)

        # Create Fixture object
        db_fixture = Fixture(
            id=fixture_id,
            date=datetime.datetime.fromtimestamp(fixture_data['fixture']['timestamp']),
            home_team_name=home_team_name,
            away_team_name=away_team_name,
            league_name=league_name
        )
        db.add(db_fixture)

        if not value_bets_found:
            print("No value bets found.")
        else:
            print(f"--- Storing {len(value_bets_found)} value bets ---")
            for bet in value_bets_found:
                db_bet = ValueBet(
                    fixture_id=fixture_id,
                    market=bet['market'],
                    bet_value=bet['value'],
                    probability=bet['prob'],
                    odds=bet['odds'],
                    value=(bet['prob'] * bet['odds'])
                )
                db.add(db_bet)

        db.commit()

    except (KeyError, TypeError) as e:
        print(f"Error processing fixture {fixture_data.get('fixture', {}).get('id', 'N/A')}. Missing data: {e}")
        db.rollback()


if __name__ == "__main__":
    # Initialize the database first. It's safe to do this even without an API key.
    print("Initializing database...")
    database.init_db()

    if not api_client.API_KEY or api_client.API_KEY == 'VotreCléApiIci':
        print("ERROR: API key not found or not set.")
        print("Please create a .env file or set environment variables.")
    else:
        db = database.SessionLocal()

        allowed_league_ids = load_allowed_leagues()
        fixtures = get_daily_fixtures()

        if fixtures:
            print(f"Found {len(fixtures)} total matches for today.")

            if allowed_league_ids:
                filtered_fixtures = [
                    f for f in fixtures if f.get('league', {}).get('id') in allowed_league_ids
                ]
                print(f"Analyzing {len(filtered_fixtures)} matches from your allowed list.")
            else:
                filtered_fixtures = fixtures

            for fixture_data in filtered_fixtures:
                analyze_and_store_fixture(db, fixture_data)

        db.close()
        print("\nData collection complete.")
