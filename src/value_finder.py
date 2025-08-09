from . import api_client

# Note: The parsing logic here is highly dependent on the actual structure
# of the API's /odds response, which is currently unknown. The code is
# written based on a plausible structure and will likely need adjustments.

def get_odds_for_fixture(fixture_id):
    """
    Fetches and parses betting odds for a specific fixture.

    Args:
        fixture_id (int): The ID of the fixture.

    Returns:
        dict: A structured dictionary of odds for target markets, or None.
    """
    endpoint = "odds"
    params = {"fixture": fixture_id}

    response = api_client.make_api_request(endpoint, params)

    if not response or not response.get('response'):
        return None

    # --- Parsing Logic ---
    # We'll try to find the specific bookmaker requested by the user (ID 8 for Bet365).
    # The structure is based on the sample response provided.
    try:
        bookmaker_data = next(
            (b for b in response['response'][0]['bookmakers'] if b['id'] == 8),
            response['response'][0]['bookmakers'][0]  # Fallback to the first available bookmaker
        )

        odds = {}
        for market in bookmaker_data['bets']:
            if market['name'] == 'Match Winner':
                odds['1x2'] = {
                    'home': float(next(v['odd'] for v in market['values'] if v['value'] == 'Home')),
                    'draw': float(next(v['odd'] for v in market['values'] if v['value'] == 'Draw')),
                    'away': float(next(v['odd'] for v in market['values'] if v['value'] == 'Away')),
                }
            elif market['name'] == 'Goals Over/Under':
                # Find the 2.5 goal line
                ou_2_5 = next((v for v in market['values'] if v['value'] == 'Over 2.5'), None)
                if ou_2_5:
                    odds['ou_2_5'] = {'over': float(ou_2_5['odd'])}
                    # Find corresponding Under 2.5
                    under_2_5 = next((v for v in market['values'] if v['value'] == 'Under 2.5'), None)
                    if under_2_5:
                        odds['ou_2_5']['under'] = float(under_2_5['odd'])

            elif market['name'] == 'Both Teams Score':
                odds['btts'] = {
                    'yes': float(next(v['odd'] for v in market['values'] if v['value'] == 'Yes')),
                    'no': float(next(v['odd'] for v in market['values'] if v['value'] == 'No')),
                }
        return odds

    except (KeyError, StopIteration, IndexError) as e:
        print(f"Could not parse odds from API response. Error: {e}")
        return None


def find_value_bets(our_probs, bookmaker_odds):
    """
    Compares our probabilities with bookmaker odds to find value bets.

    Args:
        our_probs (dict): A dictionary of our calculated probabilities for different markets.
        bookmaker_odds (dict): A dictionary of bookmaker odds for the same markets.

    Returns:
        list: A list of dictionaries, where each dictionary is a value bet.
    """
    if not our_probs or not bookmaker_odds:
        return []

    value_bets = []

    # 1X2 Market
    if '1x2' in our_probs and '1x2' in bookmaker_odds:
        if our_probs['1x2']['home_win'] * bookmaker_odds['1x2']['home'] > 1:
            value_bets.append({'market': '1X2', 'value': 'Home', 'prob': our_probs['1x2']['home_win'], 'odds': bookmaker_odds['1x2']['home']})
        if our_probs['1x2']['draw'] * bookmaker_odds['1x2']['draw'] > 1:
            value_bets.append({'market': '1X2', 'value': 'Draw', 'prob': our_probs['1x2']['draw'], 'odds': bookmaker_odds['1x2']['draw']})
        if our_probs['1x2']['away_win'] * bookmaker_odds['1x2']['away'] > 1:
            value_bets.append({'market': '1X2', 'value': 'Away', 'prob': our_probs['1x2']['away_win'], 'odds': bookmaker_odds['1x2']['away']})

    # Over/Under 2.5 Market
    if 'ou_2_5' in our_probs and 'ou_2_5' in bookmaker_odds:
        if our_probs['ou_2_5']['over'] * bookmaker_odds['ou_2_5']['over'] > 1:
            value_bets.append({'market': 'O/U 2.5', 'value': 'Over', 'prob': our_probs['ou_2_5']['over'], 'odds': bookmaker_odds['ou_2_5']['over']})
        if our_probs['ou_2_5']['under'] * bookmaker_odds['ou_2_5']['under'] > 1:
            value_bets.append({'market': 'O/U 2.5', 'value': 'Under', 'prob': our_probs['ou_2_5']['under'], 'odds': bookmaker_odds['ou_2_5']['under']})

    # BTTS Market
    if 'btts' in our_probs and 'btts' in bookmaker_odds:
        if our_probs['btts']['btts_yes'] * bookmaker_odds['btts']['yes'] > 1:
            value_bets.append({'market': 'BTTS', 'value': 'Yes', 'prob': our_probs['btts']['btts_yes'], 'odds': bookmaker_odds['btts']['yes']})
        if our_probs['btts']['btts_no'] * bookmaker_odds['btts']['no'] > 1:
            value_bets.append({'market': 'BTTS', 'value': 'No', 'prob': our_probs['btts']['btts_no'], 'odds': bookmaker_odds['btts']['no']})

    return value_bets
