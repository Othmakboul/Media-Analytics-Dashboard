from dash import Input, Output, State, callback, no_update, ctx, html
import pandas as pd
from src.data_processing import load_data, filter_data, explode_entities
from src.visualizations import (
    create_timeline, 
    create_sunburst, 
    create_cooccurrence_heatmap, 
    create_top_persons_bar,
    create_top_locations_bar,
    create_wordcloud_scatter
)

# Load data once at module level (cached)
df = load_data()

# --- Initial Setup Callbacks ---

@callback(
    Output('date-picker-range', 'min_date_allowed'),
    Output('date-picker-range', 'max_date_allowed'),
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Output('dropdown-kws', 'options'),
    Output('dropdown-loc', 'options'),
    Input('store-data-trigger', 'data') # Dummy trigger on load
)
def initialize_filters(_):
    if df.empty:
        return no_update, no_update, no_update, no_update, [], []
    
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # Get top 100 keywords for dropdown to avoid overcrowding
    all_kws = explode_entities(df, 'kws').value_counts().head(100).index.tolist()
    kw_options = [{'label': k, 'value': k} for k in all_kws]
    
    # Get top 50 locations
    all_locs = explode_entities(df, 'loc').value_counts().head(50).index.tolist()
    loc_options = [{'label': l, 'value': l} for l in all_locs]
    
    return min_date, max_date, min_date, max_date, kw_options, loc_options

# --- Cross-Filtering & Visualization Callbacks ---

@callback(
    [
        Output('kpi-total-articles', 'children'),
        Output('kpi-top-kw', 'children'),
        Output('kpi-top-person', 'children'),
        Output('kpi-top-org', 'children'),
        Output('timeline-graph', 'figure'),
        Output('top-persons-graph', 'figure'),
        Output('top-locations-graph', 'figure'),
        Output('wordcloud-graph', 'figure'),
        Output('sunburst-graph', 'figure'),
        Output('heatmap-graph', 'figure')
    ],
    [
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('dropdown-kws', 'value'),
        Input('dropdown-loc', 'value'),
        Input('filter-reset-btn', 'n_clicks'),
        # Add interactive clicks from graphs
        Input('top-persons-graph', 'clickData'),
        Input('sunburst-graph', 'clickData')
    ]
)
def update_all_charts(start_date, end_date, selected_kws, selected_locs, reset_clicks, bar_click, sunburst_click):
    """
    Main callback that updates everything based on filters.
    Handles cross-filtering priority.
    """
    # Determine what triggered the callback
    triggered_id = ctx.triggered_id
    
    # Handle Reset
    if triggered_id == 'filter-reset-btn':
        pass

    # Start with global filters
    dff = filter_data(df, start_date, end_date, selected_kws, selected_locs)
    
    # --- KPIs ---
    total_articles = f"{len(dff):,}".replace(",", " ")
    
    top_kw = "N/A"
    if not dff.empty:
        kws = explode_entities(dff, 'kws')
        if selected_kws:
            kws = kws[~kws.isin(selected_kws)]
        if not kws.empty:
            top_kw = kws.mode()[0]
            
    top_person = "N/A"
    if not dff.empty:
        pers = explode_entities(dff, 'per')
        if not pers.empty:
            top_person = pers.mode()[0]
    
    top_org = "N/A"
    if not dff.empty:
        orgs = explode_entities(dff, 'org')
        if not orgs.empty:
            top_org = orgs.mode()[0]

    # --- Charts ---
    fig_timeline = create_timeline(dff)
    fig_top_persons = create_top_persons_bar(dff)
    fig_top_locations = create_top_locations_bar(dff)
    fig_wordcloud = create_wordcloud_scatter(dff)
    fig_sunburst = create_sunburst(dff)
    fig_heatmap = create_cooccurrence_heatmap(dff)
    
    return (total_articles, top_kw, top_person, top_org, 
            fig_timeline, fig_top_persons, fig_top_locations, fig_wordcloud, 
            fig_sunburst, fig_heatmap)

# --- Reset Filter Logic (Separate for updating Input components) ---
@callback(
    Output('dropdown-kws', 'value'),
    Output('dropdown-loc', 'value'),
    Input('filter-reset-btn', 'n_clicks')
)
def reset_filters(n_clicks):
    if n_clicks:
        return [], []
    return no_update, no_update

# --- AI Analyst ---
@callback(
    Output('ai-response-area', 'children'),
    Input('ai-submit-btn', 'n_clicks'),
    State('ai-input', 'value')
)
def ai_analyst_response(n_clicks, query):
    if not n_clicks or not query:
        return "En attente de votre question..."
    
    import time
    time.sleep(1) # Simulate processing
    return html.Div([
        html.P(f"Analyse pour : '{query}'", className="mb-2 text-info"),
        html.Div([
            html.P("D'après l'analyse du corpus, voici les tendances identifiées :"),
            html.Ul([
                html.Li("Le sujet est en forte croissance ce dernier trimestre."),
                html.Li("Sentiment global mitigé avec des pics de négativité en Février."),
                html.Li("Les entités associées suggèrent un contexte géopolitique complexe.")
            ]),
            html.Small("(Réponse générée par le module de simulation IA)", className="text-muted")
        ], className="p-3 border rounded", style={'backgroundColor': 'rgba(255,255,255,0.05)', 'border': '1px solid #333'})
    ])
