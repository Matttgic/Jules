import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Value Bets du Jour",
    page_icon="⚽",
    layout="wide"
)

# --- Data Loading ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data():
    if not os.path.exists("results.json"):
        return pd.DataFrame()
    with open("results.json", "r") as f:
        data = json.load(f)
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

# --- Main App ---
st.title("⚽ Value Bets du Jour")
st.markdown("Voici les paris de valeur identifiés par l'algorithme pour les matchs à venir.")

df = load_data()

if df.empty:
    st.warning("Aucune donnée de pari disponible pour le moment. L'analyse automatique tourne une fois par jour. Veuillez réessayer plus tard.")
else:
    # --- Sidebar for Filters and Sorting ---
    st.sidebar.header("Filtres et Options")

    # Get unique leagues for the filter
    leagues = sorted(df['league'].unique())
    selected_leagues = st.sidebar.multiselect(
        "Filtrer par ligue :",
        options=leagues,
        default=leagues
    )

    # Search bar
    search_query = st.sidebar.text_input("Rechercher une équipe :")

    # Sorting options
    sort_options = {
        "Valeur (décroissant)": ("value", False),
        "Probabilité (décroissant)": ("probability", False),
        "Cote (croissant)": ("odds", True),
        "Date (plus récent)": ("timestamp", False)
    }
    sort_by_label = st.sidebar.selectbox(
        "Trier par :",
        options=list(sort_options.keys())
    )
    sort_by_col, sort_ascending = sort_options[sort_by_label]

    # --- Filtering and Sorting Data ---
    filtered_df = df[df['league'].isin(selected_leagues)]

    if search_query:
        filtered_df = filtered_df[filtered_df['match'].str.contains(search_query, case=False, na=False)]

    sorted_df = filtered_df.sort_values(by=sort_by_col, ascending=sort_ascending)

    # --- Display Logic ---
    last_update_str = sorted_df["timestamp"].max()
    last_update_dt = datetime.fromisoformat(last_update_str)
    st.info(f"Dernière mise à jour des données : {last_update_dt.strftime('%d/%m/%Y à %H:%M:%S')} UTC")

    # --- Key Metrics ---
    total_bets = len(sorted_df)
    avg_value = sorted_df['value'].mean()
    num_leagues = sorted_df['league'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Paris Trouvés", total_bets)
    col2.metric("Valeur Moyenne", f"{avg_value:.2f}")
    col3.metric("Ligues Concernées", num_leagues)

    st.subheader(f"Détail des {total_bets} paris")

    # --- DataFrame Styling ---
    def style_value(v):
        color = 'green' if v > 1.1 else 'orange' if v > 1.05 else 'black'
        return f'color: {color}; font-weight: bold;'

    display_df = sorted_df[[
        "match", "league", "market", "bet_value", "probability", "odds", "value"
    ]].copy()

    display_df.rename(columns={
        "match": "Match",
        "league": "Ligue",
        "market": "Marché",
        "bet_value": "Pari",
        "probability": "Notre Prob.",
        "odds": "Cote",
        "value": "Valeur"
    }, inplace=True)

    st.dataframe(
        display_df.style
            .format({
                "Notre Prob.": "{:.2%}",
                "Valeur": "{:.2f}"
            })
            .applymap(style_value, subset=['Valeur']),
        use_container_width=True,
        hide_index=True
    )

# --- Sidebar for Explanations ---
st.sidebar.header("Comment ça marche ?")
st.sidebar.info(
    "Ce tableau montre les paris où notre modèle estime que la probabilité de gagner "
    "est plus élevée que ce que la cote du bookmaker suggère."
)
st.sidebar.success(
    "**Valeur > 1.00** : Indique un 'value bet'. Plus la valeur est élevée, "
    "plus le modèle est confiant que la cote est avantageuse."
)
st.sidebar.warning(
    "**Avertissement :** Ceci est un outil statistique et ne garantit pas les gains. "
    "Pariez de manière responsable."
)
