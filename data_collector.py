from datetime import datetime, date
import json
from sqlalchemy.orm import Session
from src import api_client, model, probabilities, value_finder
import database
from database import Fixture, ValueBet

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

def analyze_and_store_fixture(db: Session, fixture_data: dict):
    """
    Runs the full analysis pipeline and stores the results in the database.
    """
    try:
        fixture_id = fixture_data['fixture']['id']
        fixture_date = datetime.fromtimestamp(fixture_data['fixture']['timestamp']).date()

        # Check if the fixture has already been analyzed
        existing_fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()
        if existing_fixture:
            print(f"Skipping fixture {fixture_id} (already in DB).")
            return

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
        if score_matrix is None: return

        our_probs = probabilities.get_market_probabilities(score_matrix, home_lambda, away_lambda)
        if not our_probs: return

        bookmaker_odds = value_finder.get_odds_for_fixture(fixture_id)
        if not bookmaker_odds: return

        value_bets_found = value_finder.find_value_bets(our_probs, bookmaker_odds)

        if value_bets_found:
            print(f"--- Storing {len(value_bets_found)} value bets ---")

            # Create Fixture object only if there are bets to store
            db_fixture = Fixture(
                id=fixture_id,
                date=datetime.fromtimestamp(fixture_data['fixture']['timestamp']),
                home_team_name=home_team_name,
                away_team_name=away_team_name,
                league_name=league_name
            )
            db.add(db_fixture)

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
        else:
            print("No value bets found.")

    except (KeyError, TypeError) as e:
        print(f"Error processing fixture {fixture_data.get('fixture', {}).get('id', 'N/A')}. Missing data: {e}")
        db.rollback()


if __name__ == "__main__":
    if not api_client.API_KEY or not database.DATABASE_URL:
        print("ERROR: API_KEY or DATABASE_URL not found.")
        print("Please ensure they are set as environment variables or in a .env file.")
    else:
        print("Initializing database...")
        database.init_db()
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
