import numpy as np
from scipy.stats import skellam

def calculate_1x2_probs_skellam(home_lambda, away_lambda):
    """
    Calculates Home Win (1), Draw (X), and Away Win (2) probabilities
    using the Skellam distribution. This is more accurate than matrix summation.
    """
    # The difference of two Poisson variables is a Skellam distribution.
    # We are interested in the difference k = home_goals - away_goals.
    # P(home win) = P(k > 0), P(draw) = P(k = 0), P(away win) = P(k < 0)

    draw_prob = skellam.pmf(0, mu1=home_lambda, mu2=away_lambda)
    home_win_prob = skellam.sf(0, mu1=home_lambda, mu2=away_lambda) # P(k > 0)
    away_win_prob = skellam.cdf(-1, mu1=home_lambda, mu2=away_lambda) # P(k < 0)

    return {
        "home_win": home_win_prob,
        "draw": draw_prob,
        "away_win": away_win_prob,
    }


def calculate_over_under_probs(score_matrix, threshold=2.5):
    """
    Calculates Over/Under probabilities for a given goal threshold.

    Args:
        score_matrix (np.array): A 2D numpy array of score probabilities.
        threshold (float): The goal line threshold.

    Returns:
        dict: Probabilities for {'over', 'under'}.
    """
    over_prob = 0
    under_prob = 0
    max_goals = score_matrix.shape[0] - 1

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            if i + j > threshold:
                over_prob += score_matrix[i, j]
            else:
                under_prob += score_matrix[i, j]

    total_prob = over_prob + under_prob
    if total_prob == 0: return {'over': 0, 'under': 0}

    return {
        "over": over_prob / total_prob,
        "under": under_prob / total_prob,
    }

def calculate_btts_probs(score_matrix):
    """
    Calculates Both Teams to Score (BTTS) probabilities.

    Args:
        score_matrix (np.array): A 2D numpy array of score probabilities.

    Returns:
        dict: Probabilities for {'btts_yes', 'btts_no'}.
    """
    # BTTS=No is the sum of the first row (away team didn't score) and first column (home team didn't score)
    # minus the 0-0 score, which is counted twice.
    btts_no_prob = np.sum(score_matrix[0, :]) + np.sum(score_matrix[:, 0]) - score_matrix[0, 0]

    # Normalize
    total_prob = np.sum(score_matrix)
    if total_prob == 0: return {'btts_yes': 0, 'btts_no': 0}

    btts_no_prob /= total_prob
    btts_yes_prob = 1 - btts_no_prob

    return {
        "btts_yes": btts_yes_prob,
        "btts_no": btts_no_prob,
    }

def get_market_probabilities(score_matrix, home_lambda, away_lambda):
    """
    A wrapper function to get probabilities for all target markets.
    """
    if score_matrix is None or score_matrix.size == 0:
        return None

    return {
        "1x2": calculate_1x2_probs_skellam(home_lambda, away_lambda),
        "ou_2_5": calculate_over_under_probs(score_matrix, threshold=2.5),
        "btts": calculate_btts_probs(score_matrix)
    }
