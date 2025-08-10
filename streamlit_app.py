import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

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
