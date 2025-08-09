import datetime
from src import api_client, model, probabilities, value_finder

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

def analyze_fixture(fixture):
    """
    Runs the full analysis pipeline for a single fixture.
    """
    try:
        fixture_id = fixture['fixture']['id']
        league_id = fixture['league']['id']
        season = fixture['league']['season']
        home_team_id = fixture['teams']['home']['id']
        away_team_id = fixture['teams']['away']['id']
        home_team_name = fixture['teams']['home']['name']
        away_team_name = fixture['teams']['away']['name']

        print(f"\nAnalyzing: {home_team_name} vs {away_team_name}")

        # 1. Get Poisson model probabilities
        score_matrix = model.calculate_poisson_probabilities(home_team_id, away_team_id, league_id, season)
        if score_matrix is None:
            print("Could not calculate score matrix.")
            return

        # 2. Get market probabilities
        our_probs = probabilities.get_market_probabilities(score_matrix)
        if not our_probs:
            print("Could not calculate market probabilities.")
            return

        # 3. Get bookmaker odds
        bookmaker_odds = value_finder.get_odds_for_fixture(fixture_id)
        if not bookmaker_odds:
            print("Could not retrieve odds for this fixture.")
            return

        # 4. Find value bets
        bets = value_finder.find_value_bets(our_probs, bookmaker_odds)

        if not bets:
            print("No value bets found for this match.")
        else:
            print("--- VALUE BETS FOUND ---")
            for bet in bets:
                print(
                    f"  Market: {bet['market']} | Bet: {bet['value']} | "
                    f"Our Prob: {bet['prob']:.2%} | Odds: {bet['odds']}"
                )

    except (KeyError, TypeError) as e:
        print(f"Error processing fixture {fixture.get('fixture', {}).get('id', 'N/A')}. Missing data: {e}")


if __name__ == "__main__":
    # A FAKE API KEY IS NEEDED FOR THE SCRIPT TO RUN.
    # The user needs to create a .env file with their actual key.
    if not api_client.API_KEY or api_client.API_KEY == 'VotreCléApiIci':
        print("ERROR: API key not found or not set.")
        print("Please create a .env file in the root directory with your RapidAPI key:")
        print("API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    else:
        fixtures = get_daily_fixtures()
        if fixtures:
            print(f"Found {len(fixtures)} matches to analyze.")
            for fixture_data in fixtures:
                analyze_fixture(fixture_data)
        print("\nAnalysis complete.")
