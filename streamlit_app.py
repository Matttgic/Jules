import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import database
from database import ValueBet, Fixture

# --- Page Configuration ---
st.set_page_config(
    page_title="Value Bets Historique",
    page_icon="⚽",
    layout="wide"
)

# --- Data Loading ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data():
    """Loads all historical value bets from the database."""
    db = database.SessionLocal()
    try:
        # Query for value bets, joining with fixtures to get match details
        query = db.query(ValueBet).join(Fixture).order_by(Fixture.date.desc())

        # Use pandas to read the SQL query directly into a DataFrame
        df = pd.read_sql(query.statement, db.bind)
        if not df.empty:
            # We need to get fixture details into the main df for filtering/display
            fixtures_df = pd.read_sql(db.query(Fixture).statement, db.bind)
            fixtures_df = fixtures_df.rename(columns={'id': 'fixture_id', 'date': 'match_date'})
            df = pd.merge(df, fixtures_df, on='fixture_id')
    finally:
        db.close()

    return df

# --- Main App ---
st.title("⚽ Historique & Bilan des Value Bets")
st.markdown("Analyse de la performance de l'algorithme au fil du temps.")

df = load_data()

if df.empty:
    st.warning("Aucune donnée de pari disponible dans la base de données. L'analyse automatique n'a peut-être pas encore tourné.")
else:
    # --- Sidebar for Filters and Sorting ---
    st.sidebar.header("Filtres et Options")

    # Get unique leagues for the filter
    leagues = sorted(df['league_name'].unique())
    selected_leagues = st.sidebar.multiselect(
        "Filtrer par ligue :",
        options=leagues,
        default=leagues
    )

    # Search bar
    search_query = st.sidebar.text_input("Rechercher une équipe :")

    # Sorting options
    sort_options = {
        "Date (plus récent)": ("match_date", False),
        "Valeur (décroissant)": ("value", False),
        "Probabilité (décroissant)": ("probability", False),
        "Cote (croissant)": ("odds", True),
    }
    sort_by_label = st.sidebar.selectbox(
        "Trier par :",
        options=list(sort_options.keys())
    )
    sort_by_col, sort_ascending = sort_options[sort_by_label]

    # --- Filtering and Sorting Data ---
    filtered_df = df[df['league_name'].isin(selected_leagues)]

    if search_query:
        # Create a combined match string for searching
        match_search_str = df['home_team_name'] + ' vs ' + df['away_team_name']
        filtered_df = filtered_df[match_search_str.str.contains(search_query, case=False, na=False)]

    sorted_df = filtered_df.sort_values(by=sort_by_col, ascending=sort_ascending)

    # --- Display Logic ---
    st.info(f"Affichage de {len(sorted_df)} paris sur un total de {len(df)}.")

    # --- Key Metrics ---
    total_bets = len(sorted_df)
    avg_value = sorted_df['value'].mean() if total_bets > 0 else 0
    num_leagues = sorted_df['league_name'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Paris Affichés", total_bets)
    col2.metric("Valeur Moyenne", f"{avg_value:.2f}")
    col3.metric("Ligues Concernées", num_leagues)

    st.subheader("Détail des Paris")

    # --- DataFrame Styling ---
    def style_value(v):
        color = 'green' if v > 1.1 else 'orange' if v > 1.05 else 'black'
        return f'color: {color}; font-weight: bold;'

    # Create match string for display
    sorted_df['Match'] = sorted_df['home_team_name'] + ' vs ' + sorted_df['away_team_name']

    display_df = sorted_df[[
        "Match", "league_name", "market", "bet_value", "probability", "odds", "value"
    ]].copy()

    display_df.rename(columns={
        "league_name": "Ligue",
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
            .apply(lambda x: x.map(style_value), subset=['Valeur']),
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
