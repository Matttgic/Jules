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

# --- Title ---
st.title("⚽ Value Bets du Jour")
st.markdown("Voici les paris de valeur identifiés par l'algorithme pour les matchs à venir.")

# --- Data Loading ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data():
    if not os.path.exists("results.json"):
        return pd.DataFrame(), None

    with open("results.json", "r") as f:
        data = json.load(f)

    if not data:
        return pd.DataFrame(), None

    df = pd.DataFrame(data)

    # Get the timestamp of the last update from the first record
    last_update_str = df["timestamp"].max()
    last_update_dt = datetime.fromisoformat(last_update_str)

    return df, last_update_dt

df, last_update = load_data()

# --- Display Logic ---
if df.empty:
    st.warning("Aucune donnée de pari disponible pour le moment. L'analyse automatique tourne une fois par jour. Veuillez réessayer plus tard.")
else:
    # --- Display Last Update Time ---
    st.info(f"Dernière mise à jour des données : {last_update.strftime('%d/%m/%Y à %H:%M:%S')} UTC")

    # --- Data Display ---
    st.subheader("Paris Identifiés")

    # Format dataframe for display
    display_df = df[[
        "match", "league", "market", "bet_value", "probability", "odds", "value"
    ]].copy() # Create a copy to avoid SettingWithCopyWarning

    display_df["probability"] = display_df["probability"].map(lambda p: f"{p:.2%}")
    display_df["value"] = display_df["value"].map(lambda v: f"{v:.2f}")

    # Rename columns for clarity in French
    display_df.rename(columns={
        "match": "Match",
        "league": "Ligue",
        "market": "Marché",
        "bet_value": "Pari",
        "probability": "Notre Prob.",
        "odds": "Cote",
        "value": "Valeur"
    }, inplace=True)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

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
