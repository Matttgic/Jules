import pandas as pd
import numpy as np

def _calculate_grouped_stats(df, group_by_col, sort_by='ROI'):
    """
    Generic function to calculate performance statistics (ROI, Win Rate, Profit)
    for a given column.

    Args:
        df (pd.DataFrame): The DataFrame of settled bets.
        group_by_col (str): The column name to group the data by.
        sort_by (str): The column to sort the results by.

    Returns:
        pd.DataFrame: A DataFrame with aggregated statistics for each category.
    """
    if df.empty or group_by_col not in df.columns:
        return pd.DataFrame()

    def calculate_metrics(group):
        """Calculates performance metrics for a single group of bets."""
        settled = len(group)
        if settled == 0:
            return pd.Series({
                'Paris': 0, 'Taux de Victoire': 0, 'Profit (u)': 0, 'ROI': 0
            })

        wins = group[group['outcome'] == 'Win']
        losses = group[group['outcome'] == 'Loss']

        win_rate = len(wins) / settled
        # Profit is calculated assuming a 1 unit stake on each bet
        profit = (wins['odds'] - 1).sum() - len(losses)
        roi = profit / settled

        return pd.Series({
            'Paris': settled,
            'Taux de Victoire': win_rate,
            'Profit (u)': profit,
            'ROI': roi
        })

    stats_df = df.groupby(group_by_col, observed=True).apply(calculate_metrics)
    stats_df = stats_df.sort_values(by=sort_by, ascending=False).reset_index()

    return stats_df

def get_stats_by_league(df, min_bets=10):
    """
    Calculates and filters statistics per league.

    Args:
        df (pd.DataFrame): Settled bets DataFrame.
        min_bets (int): Minimum number of bets for a league to be included.

    Returns:
        pd.DataFrame: Statistics per league.
    """
    stats = _calculate_grouped_stats(df, 'league')
    stats = stats[stats['Paris'] >= min_bets]
    return stats.rename(columns={'league': 'Ligue'})

def get_stats_by_market(df):
    """Calculates statistics per bet type (market)."""
    return _calculate_grouped_stats(df, 'market').rename(columns={'market': 'Type de Pari'})

def get_stats_by_odds_range(df):
    """Calculates statistics per odds range."""
    bins = [1, 1.5, 2.0, 2.5, 3.0, 4.0, np.inf]
    labels = ['1.0-1.5', '1.5-2.0', '2.0-2.5', '2.5-3.0', '3.0-4.0', '4.0+']
    df_copy = df.copy()
    df_copy['odds_range'] = pd.cut(df_copy['odds'], bins=bins, labels=labels, right=False)
    return _calculate_grouped_stats(df_copy, 'odds_range').rename(columns={'odds_range': 'Tranche de Cotes'})

def get_stats_by_value_range(df):
    """
    Calculates statistics per value range.
    Value is defined as (probability * odds) and must be > 1.
    """
    bins = [1.0, 1.1, 1.2, 1.4, 1.6, 2.0, np.inf]
    labels = ['1.0-1.1', '1.1-1.2', '1.2-1.4', '1.4-1.6', '1.6-2.0', '2.0+']
    df_copy = df.copy()
    df_copy['value_range'] = pd.cut(df_copy['value'], bins=bins, labels=labels, right=False)
    return _calculate_grouped_stats(df_copy, 'value_range').rename(columns={'value_range': 'Tranche de Valeur'})

def get_stats_by_prob_range(df):
    """Calculates statistics per probability range."""
    bins = [0, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01] # Use 1.01 to include 1.0
    labels = ['<40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
    df_copy = df.copy()
    df_copy['prob_range'] = pd.cut(df_copy['probability'], bins=bins, labels=labels, right=False)
    return _calculate_grouped_stats(df_copy, 'prob_range').rename(columns={'prob_range': 'Tranche de Proba'})
