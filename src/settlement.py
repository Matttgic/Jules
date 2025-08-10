def settle_bet(bet: dict, final_score: dict) -> str:
    """
    Determines the outcome of a bet given the final score.

    Args:
        bet (dict): The bet object from our history file.
        final_score (dict): The final score object from the API, e.g., {'home': 2, 'away': 1}.

    Returns:
        str: "Win", "Loss", or "Push".
    """
    market = bet.get("market")
    bet_value = bet.get("bet_value")
    home_score = final_score.get("home")
    away_score = final_score.get("away")

    if home_score is None or away_score is None:
        return None # Score is not available

    if market == "1X2":
        if bet_value == "Home" and home_score > away_score:
            return "Win"
        elif bet_value == "Away" and away_score > home_score:
            return "Win"
        elif bet_value == "Draw" and home_score == away_score:
            return "Win"
        else:
            return "Loss"

    elif market == "O/U 2.5":
        total_goals = home_score + away_score
        threshold = 2.5
        if bet_value == "Over" and total_goals > threshold:
            return "Win"
        elif bet_value == "Under" and total_goals < threshold:
            return "Win"
        elif total_goals == threshold:
            return "Push"
        else:
            return "Loss"

    elif market == "BTTS":
        if bet_value == "Yes" and home_score > 0 and away_score > 0:
            return "Win"
        elif bet_value == "No" and (home_score == 0 or away_score == 0):
            return "Win"
        else:
            return "Loss"

    return None # Market not supported
