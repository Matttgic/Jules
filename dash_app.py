import dash
import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc, Input, Output, State
import pandas as pd
import json
import os
from src import statistics

# --- Data Loading and Preparation ---
HISTORY_FILE = "history.json"

def load_data():
    """Loads all historical value bets from the history file."""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()
    with open(HISTORY_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return pd.DataFrame()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def prepare_data(df):
    """Prepares the dataframe for display and filtering."""
    if df.empty:
        return df

    if 'match_date' in df.columns:
        match_dates_dt = pd.to_datetime(df['match_date'], errors='coerce', utc=True)
        timestamps_dt = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
        df['display_date_dt'] = match_dates_dt.fillna(timestamps_dt)
    else:
        df['display_date_dt'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)

    df.dropna(subset=['display_date_dt'], inplace=True)
    df['Date'] = df['display_date_dt'].dt.strftime('%Y-%m-%d %H:%M')

    df.rename(columns={
        "match": "Match", "league": "Ligue", "market": "Marché",
        "bet_value": "Pari", "probability": "Notre Prob.", "odds": "Cote",
        "value": "Valeur", "outcome": "Résultat"
    }, inplace=True)

    df['Résultat'] = df['Résultat'].fillna('En attente')
    return df

# Load and prepare data once at startup
df_raw = load_data()
df_prepared = prepare_data(df_raw.copy())

# --- App Layout ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

def build_stats_card(title, metric_val, metric_label, data, id_suffix):
    """Helper function to build a statistics card with a metric and a table."""
    return dbc.Card([
        dbc.CardHeader(html.H5(title, className="m-0")),
        dbc.CardBody([
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.H3(metric_val, id=f"metric-val-{id_suffix}"),
                        html.P(metric_label, id=f"metric-label-{id_suffix}", className="text-muted"),
                    ])
                )
            ),
            html.Div(id=f"stats-table-{id_suffix}", children=dash_table.DataTable(data=data))
        ])
    ], className="mb-3")

app.layout = dbc.Container([
    html.H1("Bilan & Historique des Value Bets (Dash Version)"),
    html.Hr(),

    dbc.Row([
        # --- Control Panel ---
        dbc.Col([
            dbc.Card([
                html.Div([
                    dbc.Label("Filtrer par ligue :"),
                    dcc.Dropdown(
                        id='league-filter',
                        options=[{'label': i, 'value': i} for i in sorted(df_prepared['Ligue'].unique())],
                        value=list(df_prepared['Ligue'].unique()),
                        multi=True,
                    ),
                ]),
                html.Div([
                    dbc.Label("Rechercher une équipe :", className="mt-3"),
                    dbc.Input(id='team-search', type='text', placeholder='Entrez un nom d\'équipe...'),
                ]),
            ], body=True),
            html.Hr(),
            # --- Overall Performance ---
            html.H4("Bilan de Performance (sur les paris terminés)"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.P("Paris Terminés"), html.H4(id="metric-total-settled")]))),
                dbc.Col(dbc.Card(dbc.CardBody([html.P("Taux de Victoire"), html.H4(id="metric-win-rate")]))),
                dbc.Col(dbc.Card(dbc.CardBody([html.P("Gain/Perte (u)"), html.H4(id="metric-profit")]))),
                dbc.Col(dbc.Card(dbc.CardBody([html.P("ROI"), html.H4(id="metric-roi")]))),
            ]),

        ], md=4),

        # --- Main History Table ---
        dbc.Col(
            dash_table.DataTable(
                id='history-table',
                columns=[{"name": i, "id": i} for i in ["Date", "Match", "Ligue", "Marché", "Pari", "Notre Prob.", "Cote", "Valeur", "Résultat"]],
                style_cell={'textAlign': 'left', 'fontFamily': 'sans-serif'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'column_id': 'Résultat', 'filter_query': '{Résultat} = "Win"'}, 'color': 'green', 'fontWeight': 'bold'},
                    {'if': {'column_id': 'Résultat', 'filter_query': '{Résultat} = "Loss"'}, 'color': 'red', 'fontWeight': 'bold'},
                    {'if': {'column_id': 'Résultat', 'filter_query': '{Résultat} = "Push"'}, 'color': 'grey', 'fontWeight': 'bold'},
                ],
                page_size=15,
                sort_action="native",
            ),
            md=8,
        ),
    ]),

    html.Hr(),
    # --- Detailed Statistics ---
    html.H2("Analyses Détaillées"),
    dbc.Accordion(
        [
            dbc.AccordionItem(build_stats_card("Par Ligue (Top 10)", "-", "Roi des Ligues", [], "league"), title="👑 Par Ligue"),
            dbc.AccordionItem(build_stats_card("Par Type de Pari", "-", "Roi des Marchés", [], "market"), title="👑 Par Type de Pari"),
            dbc.AccordionItem(build_stats_card("Par Tranche de Cotes", "-", "Reine des Cotes", [], "odds"), title="👑 Par Tranche de Cotes"),
            dbc.AccordionItem(build_stats_card("Par Tranche de Valeur", "-", "Reine de la Valeur", [], "value"), title="👑 Par Tranche de Valeur"),
            dbc.AccordionItem(build_stats_card("Par Tranche de Probabilité", "-", "Reine de la Proba", [], "prob"), title="👑 Par Tranche de Probabilité"),
        ],
        start_collapsed=True,
    )
], fluid=True)

# --- Callbacks ---
@app.callback(
    [Output('history-table', 'data'),
     Output('metric-total-settled', 'children'),
     Output('metric-win-rate', 'children'),
     Output('metric-profit', 'children'),
     Output('metric-roi', 'children'),
     Output('metric-val-league', 'children'), Output('metric-label-league', 'children'), Output('stats-table-league', 'children'),
     Output('metric-val-market', 'children'), Output('metric-label-market', 'children'), Output('stats-table-market', 'children'),
     Output('metric-val-odds', 'children'), Output('metric-label-odds', 'children'), Output('stats-table-odds', 'children'),
     Output('metric-val-value', 'children'), Output('metric-label-value', 'children'), Output('stats-table-value', 'children'),
     Output('metric-val-prob', 'children'), Output('metric-label-prob', 'children'), Output('stats-table-prob', 'children'),
     ],
    [Input('league-filter', 'value'),
     Input('team-search', 'value')]
)
def update_outputs(selected_leagues, search_query):
    # --- Filter Data ---
    filtered_df = df_prepared[df_prepared['Ligue'].isin(selected_leagues)]
    if search_query:
        filtered_df = filtered_df[filtered_df['Match'].str.contains(search_query, case=False, na=False)]

    sorted_df = filtered_df.sort_values(by="display_date_dt", ascending=False)

    # --- Calculate Overall Metrics ---
    settled_bets = sorted_df.dropna(subset=['Résultat'])
    total_settled = len(settled_bets)
    if total_settled > 0:
        wins = settled_bets[settled_bets['Résultat'] == 'Win']
        losses = settled_bets[settled_bets['Résultat'] == 'Loss']
        win_rate = f"{len(wins) / total_settled:.2%}"
        profit = (wins['Cote'] - 1).sum() - len(losses)
        roi = f"{(profit / total_settled):.2%}"
        profit_str = f"{profit:+.2f} u"
    else:
        win_rate, profit_str, roi = "0.00%", "0.00 u", "0.00%"

    # --- Calculate Detailed Stats ---
    def generate_stats_output(stats_df, key_col, king_prefix):
        if not stats_df.empty:
            top_performer = stats_df.iloc[0]
            metric_val = f"{top_performer['ROI']:.2%}"
            metric_label = f"{king_prefix}: {top_performer[key_col]}"
            table = dash_table.DataTable(
                data=stats_df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in stats_df.columns],
                style_cell={'textAlign': 'left'},
                style_data_conditional=[{'if': {'filter_query': '{ROI} > 0', 'column_id': 'ROI'}, 'color': 'green'},
                                        {'if': {'filter_query': '{ROI} < 0', 'column_id': 'ROI'}, 'color': 'red'}],
                style_header={'backgroundColor': 'rgb(240, 240, 240)', 'fontWeight': 'bold'},
            )
            return metric_val, metric_label, table
        return "-", king_prefix, None

    league_stats = statistics.get_stats_by_league(settled_bets, min_bets=10).head(10)
    mv_league, ml_league, table_league = generate_stats_output(league_stats, 'Ligue', "Roi des Ligues")

    market_stats = statistics.get_stats_by_market(settled_bets)
    mv_market, ml_market, table_market = generate_stats_output(market_stats, 'Type de Pari', "Roi des Marchés")

    odds_stats = statistics.get_stats_by_odds_range(settled_bets)
    mv_odds, ml_odds, table_odds = generate_stats_output(odds_stats, 'Tranche de Cotes', "Reine des Cotes")

    value_stats = statistics.get_stats_by_value_range(settled_bets)
    mv_value, ml_value, table_value = generate_stats_output(value_stats, 'Tranche de Valeur', "Reine de la Valeur")

    prob_stats = statistics.get_stats_by_prob_range(settled_bets)
    mv_prob, ml_prob, table_prob = generate_stats_output(prob_stats, 'Tranche de Proba', "Reine de la Proba")

    return (
        sorted_df.to_dict('records'),
        total_settled, win_rate, profit_str, roi,
        mv_league, ml_league, table_league,
        mv_market, ml_market, table_market,
        mv_odds, ml_odds, table_odds,
        mv_value, ml_value, table_value,
        mv_prob, ml_prob, table_prob,
    )

if __name__ == '__main__':
    app.run_server(debug=True)
