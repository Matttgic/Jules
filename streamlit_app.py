import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from src import statistics

HISTORY_FILE = "history.json"

# --- Page Configuration ---
st.set_page_config(
    page_title="Value Bets Bilan",
    page_icon="⚽",
    layout="wide"
)

# --- Data Loading ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data():
    """Loads all historical value bets from the history file."""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()

    with open(HISTORY_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return pd.DataFrame() # Return empty df if file is corrupt/empty

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)

# --- Main App ---
st.title("⚽ Bilan & Historique des Value Bets")
st.markdown("Analyse de la performance de l'algorithme au fil du temps.")

df = load_data()

if df.empty:
    st.warning("Aucune donnée de pari disponible. Le fichier d'historique est vide ou n'existe pas. L'analyse automatique n'a peut-être pas encore tourné.")
else:
    # --- Sidebar for Filters and Sorting ---
    st.sidebar.header("Filtres et Options")
    leagues = sorted(df['league'].unique())
    selected_leagues = st.sidebar.multiselect("Filtrer par ligue :", options=leagues, default=leagues)
    search_query = st.sidebar.text_input("Rechercher une équipe :")
    sort_options = {
        "Date (plus récent)": ("timestamp", False),
        "Valeur (décroissant)": ("value", False),
    }
    sort_by_label = st.sidebar.selectbox("Trier par :", options=list(sort_options.keys()))
    sort_by_col, sort_ascending = sort_options[sort_by_label]

    # --- Filtering and Sorting Data ---
    filtered_df = df[df['league'].isin(selected_leagues)]
    if search_query:
        filtered_df = filtered_df[filtered_df['match'].str.contains(search_query, case=False, na=False)]
    sorted_df = filtered_df.sort_values(by=sort_by_col, ascending=sort_ascending)

    # --- Performance Metrics Calculation ---
    settled_bets = sorted_df.dropna(subset=['outcome'])
    total_settled = len(settled_bets)
    wins = settled_bets[settled_bets['outcome'] == 'Win']
    losses = settled_bets[settled_bets['outcome'] == 'Loss']
    pushes = settled_bets[settled_bets['outcome'] == 'Push']

    win_rate = len(wins) / total_settled if total_settled > 0 else 0

    # Calculate profit/loss assuming 1 unit stake
    profit = (wins['odds'] - 1).sum() - len(losses)
    roi = (profit / total_settled) if total_settled > 0 else 0

    # --- Display Logic ---
    st.header("Bilan de Performance (sur les paris terminés)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Paris Terminés", total_settled)
    col2.metric("Taux de Victoire", f"{win_rate:.2%}")
    col3.metric("Unités de Gain/Perte", f"{profit:+.2f} u")
    col4.metric("ROI", f"{roi:.2%}")

    st.header("Historique des Paris")

    # --- DataFrame Styling ---
    def style_outcome(outcome):
        if pd.isna(outcome): return ''
        color = 'green' if outcome == 'Win' else 'red' if outcome == 'Loss' else 'grey'
        return f'color: {color}; font-weight: bold;'

    display_df = sorted_df[[
        "match", "league", "market", "bet_value", "probability", "odds", "value", "outcome"
    ]].copy()
    display_df.rename(columns={
        "match": "Match", "league": "Ligue", "market": "Marché",
        "bet_value": "Pari", "probability": "Notre Prob.", "odds": "Cote",
        "value": "Valeur", "outcome": "Résultat"
    }, inplace=True)

    # Fill NaN for display
    display_df['Résultat'] = display_df['Résultat'].fillna('En attente')

    st.dataframe(
        display_df.style
            .format({"Notre Prob.": "{:.2%}", "Valeur": "{:.2f}", "Cote": "{:.2f}"})
            .apply(lambda x: x.map(style_outcome), subset=['Résultat']),
        use_container_width=True,
        hide_index=True
    )

    # --- Detailed Statistics Section ---
    st.header("Analyses Détaillées")
    st.markdown("Analyses de performance par catégorie pour identifier les paris les plus et les moins rentables.")

    with st.expander("Voir les analyses détaillées", expanded=True):
        # Helper function to style the stats tables
        def style_stats_df(df):
            # sourcery skip: hide_index
            return df.style.format({
                'Taux de Victoire': '{:.2%}',
                'ROI': '{:.2%}',
                'Profit (u)': '{:+.2f}'
            }).background_gradient(
                cmap='RdYlGn', subset=['ROI'], vmin=-0.5, vmax=0.5
            ).hide_index()

        # Calculate stats only on settled bets
        settled_df = sorted_df.dropna(subset=['outcome'])

        if settled_df.empty:
            st.info("Aucun pari terminé à analyser pour les statistiques détaillées.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("👑 Par Ligue (Top 10)")
                league_stats = statistics.get_stats_by_league(settled_df, min_bets=10)
                if not league_stats.empty:
                    top_league = league_stats.iloc[0]
                    st.metric(
                        f"Roi des Ligues : {top_league['Ligue']}",
                        f"{top_league['ROI']:.2%}",
                        f"{top_league['Profit (u)']:.2f}u en {top_league['Paris']} paris"
                    )
                    st.dataframe(style_stats_df(league_stats.head(10)), use_container_width=True)
                else:
                    st.info("Pas assez de données par ligue (min 10 paris).")

                st.subheader("👑 Par Type de Pari")
                market_stats = statistics.get_stats_by_market(settled_df)
                if not market_stats.empty:
                    top_market = market_stats.iloc[0]
                    st.metric(
                        f"Roi des Marchés : {top_market['Type de Pari']}",
                        f"{top_market['ROI']:.2%}",
                        f"{top_market['Profit (u)']:.2f}u en {top_market['Paris']} paris"
                    )
                    st.dataframe(style_stats_df(market_stats), use_container_width=True)
                else:
                    st.info("Aucune donnée de marché.")


            with col2:
                st.subheader("👑 Par Tranche de Cotes")
                odds_stats = statistics.get_stats_by_odds_range(settled_df)
                if not odds_stats.empty:
                    top_odds = odds_stats.iloc[0]
                    st.metric(
                        f"Reine des Cotes : {top_odds['Tranche de Cotes']}",
                        f"{top_odds['ROI']:.2%}",
                        f"{top_odds['Profit (u)']:.2f}u en {top_odds['Paris']} paris"
                    )
                    st.dataframe(style_stats_df(odds_stats), use_container_width=True)
                else:
                    st.info("Aucune donnée de cote.")


                st.subheader("👑 Par Tranche de Valeur")
                value_stats = statistics.get_stats_by_value_range(settled_df)
                if not value_stats.empty:
                    top_value = value_stats.iloc[0]
                    st.metric(
                        f"Reine de la Valeur : {top_value['Tranche de Valeur']}",
                        f"{top_value['ROI']:.2%}",
                        f"{top_value['Profit (u)']:.2f}u en {top_value['Paris']} paris"
                    )
                    st.dataframe(style_stats_df(value_stats), use_container_width=True)
                else:
                    st.info("Aucune donnée de valeur.")

            # Probability stats can take the full width
            st.subheader("👑 Par Tranche de Probabilité")
            prob_stats = statistics.get_stats_by_prob_range(settled_df)
            if not prob_stats.empty:
                top_prob = prob_stats.iloc[0]
                st.metric(
                    f"Reine de la Proba : {top_prob['Tranche de Proba']}",
                    f"{top_prob['ROI']:.2%}",
                    f"{top_prob['Profit (u)']:.2f}u en {top_prob['Paris']} paris"
                )
                st.dataframe(style_stats_df(prob_stats), use_container_width=True)
            else:
                st.info("Aucune donnée de probabilité.")


# --- Sidebar for Explanations ---
st.sidebar.header("Comment ça marche ?")
st.sidebar.info(
    "Ce tableau montre l'historique des paris où notre modèle a estimé que la probabilité de gagner "
    "était plus élevée que ce que la cote du bookmaker suggérait."
)
st.sidebar.success(
    "**Valeur > 1.00** : Indique un 'value bet'. Plus la valeur est élevée, "
    "plus le modèle est confiant que la cote est avantageuse."
)
st.sidebar.warning(
    "**Avertissement :** Ceci est un outil statistique et ne garantit pas les gains. "
    "Pariez de manière responsable."
)
