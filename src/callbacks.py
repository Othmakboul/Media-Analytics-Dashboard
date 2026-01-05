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
from src.ai_service import get_ai_service
import dash_bootstrap_components as dbc
from datetime import datetime

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
    Output('ai-chat-history', 'data'),
    Output('ai-input', 'value'),
    Input('ai-submit-btn', 'n_clicks'),
    State('ai-input', 'value'),
    State('ai-chat-history', 'data'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('dropdown-kws', 'value'),
    State('dropdown-loc', 'value'),
    prevent_initial_call=True
)
def ai_analyst_query(n_clicks, query, chat_history, start_date, end_date, selected_kws, selected_locs):
    """
    Context-aware AI callback that uses Groq API.
    Filters data based on current dashboard state and sends to AI.
    """
    if not query or not query.strip():
        return no_update, no_update

    # Initialize chat history if None
    if chat_history is None:
        chat_history = []

    try:
        # Filter data based on current dashboard state
        filtered_df = filter_data(df, start_date, end_date, selected_kws, selected_locs)

        # Prepare filter info for context
        filters = {
            'start_date': start_date,
            'end_date': end_date,
            'keywords': selected_kws or [],
            'locations': selected_locs or []
        }

        # Get AI service instance
        ai_service = get_ai_service()

        # Prepare data context
        context = ai_service.prepare_data_context(filtered_df, filters)

        # Generate AI response
        result = ai_service.generate_response(query, context)

        # Add user message to history
        chat_history.append({
            'role': 'user',
            'content': query,
            'timestamp': datetime.now().isoformat()
        })

        # Add AI response to history
        if result['success']:
            chat_history.append({
                'role': 'assistant',
                'content': result['message'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Add error message
            chat_history.append({
                'role': 'error',
                'content': result['message'],
                'timestamp': datetime.now().isoformat()
            })

        # Clear input and return updated history
        return chat_history, ""

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Erreur lors de la génération de la réponse : {str(e)}"
        chat_history.append({
            'role': 'user',
            'content': query,
            'timestamp': datetime.now().isoformat()
        })
        chat_history.append({
            'role': 'error',
            'content': error_msg,
            'timestamp': datetime.now().isoformat()
        })
        return chat_history, ""


@callback(
    Output('ai-chat-history-display', 'children'),
    Input('ai-chat-history', 'data')
)
def display_chat_history(chat_history):
    """
    Displays the chat history in a formatted way.
    """
    if not chat_history:
        return html.P(
            "Aucun message. Posez une question pour commencer !",
            className="text-muted text-center",
            style={'marginTop': '100px'}
        )

    messages = []
    for msg in chat_history:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', '')

        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = ''

        if role == 'user':
            # User message (right-aligned, blue)
            message_div = html.Div([
                html.Div([
                    html.Small(time_str, className="text-muted d-block mb-1"),
                    html.Div(content, className="p-2 rounded", style={
                        'backgroundColor': '#0d6efd',
                        'color': '#fff',
                        'display': 'inline-block',
                        'maxWidth': '80%'
                    })
                ], style={'textAlign': 'right'})
            ], className="mb-3")
        elif role == 'assistant':
            # AI message (left-aligned, green)
            message_div = html.Div([
                html.Div([
                    html.Small(time_str, className="text-muted d-block mb-1"),
                    dbc.Alert(content, color="success", className="mb-0", style={
                        'whiteSpace': 'pre-wrap',
                        'maxWidth': '90%',
                        'display': 'inline-block'
                    })
                ], style={'textAlign': 'left'})
            ], className="mb-3")
        else:  # error
            # Error message (left-aligned, red)
            message_div = html.Div([
                html.Div([
                    html.Small(time_str, className="text-muted d-block mb-1"),
                    dbc.Alert(content, color="danger", className="mb-0", style={
                        'maxWidth': '90%',
                        'display': 'inline-block'
                    })
                ], style={'textAlign': 'left'})
            ], className="mb-3")

        messages.append(message_div)

    return messages


@callback(
    Output('ai-chat-history', 'data', allow_duplicate=True),
    Input('ai-clear-history-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_chat_history(n_clicks):
    """
    Clears the chat history when the clear button is clicked.
    """
    return []
