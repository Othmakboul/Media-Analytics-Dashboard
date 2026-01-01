from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import date

# Icons or specialized components could be added here

def create_sidebar():
    return html.Div(
        [
            html.H2("Media Analytics", className="display-6", style={'color': '#fff'}),
            html.Hr(),
            html.P("Filtres Globaux", className="lead"),
            
            # Date Range Picker
            html.Label("Période d'analyse", className="mt-3"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=date(2020, 1, 1), # Default placeholder, will be updated by callback
                end_date=date.today(),
                display_format='DD/MM/YYYY',
                className='mb-3 w-100',
                style={'border': 'none'}
            ),
            
            # Keywords Filter
            html.Label("Mots-clés Principaux", className="mt-3"),
            dcc.Dropdown(
                id='dropdown-kws',
                multi=True,
                placeholder="Sélectionner des mots-clés...",
                className="mb-3 text-dark", # text-dark for readability in dark mode dropdowns
                style={'color': '#000'} 
            ),
            
            # Locations Filter
            html.Label("Zones Géographiques", className="mt-3"),
            dcc.Dropdown(
                id='dropdown-loc',
                multi=True,
                placeholder="Sélectionner des lieux...",
                className="mb-3 text-dark",
                style={'color': '#000'}
            ),
            
            html.Hr(),
            
            # Reset Button
            dbc.Button(
                "Réinitialiser les filtres", 
                id="filter-reset-btn", 
                color="danger", 
                outline=True, 
                className="w-100 mt-3"
            ),
            
            html.Div(
                [
                    html.Small("Développé pour l'analyse de corpus de presse.", className="text-muted mt-5 d-block"),
                ],
                style={'marginTop': 'auto'}
            )
        ],
        className="sidebar"
    )

def create_kpi_cards():
    return dbc.Row(
        [
            dbc.Col(
                html.Div([
                    html.H6("Total Articles", className="kpi-title"),
                    html.H3("...", id="kpi-total-articles", className="kpi-value")
                ], className="glass-card p-3 h-100 kpi-card"),
                width=3
            ),
            dbc.Col(
                html.Div([
                    html.H6("Top Mot-clé", className="kpi-title"),
                    html.H3("...", id="kpi-top-kw", className="kpi-value")
                ], className="glass-card p-3 h-100 kpi-card"),
                width=3
            ),
            dbc.Col(
                html.Div([
                    html.H6("Top Personnalité", className="kpi-title"),
                    html.H3("...", id="kpi-top-person", className="kpi-value")
                ], className="glass-card p-3 h-100 kpi-card"),
                width=3
            ),
            dbc.Col(
                html.Div([
                    html.H6("Top Organisation", className="kpi-title"),
                    html.H3("...", id="kpi-top-org", className="kpi-value")
                ], className="glass-card p-3 h-100 kpi-card"),
                width=3
            ),
        ],
        className="mb-4"
    )

def create_tabs_content():
    return dbc.Tabs(
        [
            dbc.Tab(label="Vue d'ensemble", tab_id="tab-overview", children=[
                html.Div([
                    # Timeline
                    dbc.Row([
                        dbc.Col(dcc.Loading(dcc.Graph(id='timeline-graph', config={'displayModeBar': False}), color="#00bc8c", type="circle"), width=12)
                    ], className="mb-4 glass-card p-2"),
                    
                    # Word Cloud and Top Persons side by side
                    dbc.Row([
                        dbc.Col(dcc.Loading(dcc.Graph(id='wordcloud-graph', config={'displayModeBar': False}), color="#00bc8c"), width=6),
                        dbc.Col(dcc.Loading(dcc.Graph(id='top-persons-graph', config={'displayModeBar': False}), color="#00bc8c"), width=6)
                    ], className="mb-4 glass-card p-2"),
                    
                    # Top Locations
                    dbc.Row([
                        dbc.Col(dcc.Loading(dcc.Graph(id='top-locations-graph', config={'displayModeBar': False}), color="#00bc8c"), width=12)
                    ], className="glass-card p-2")
                ], className="pt-3")
            ]),
            
            dbc.Tab(label="Exploration Entités", tab_id="tab-entities", children=[
                html.Div([
                    dbc.Row([
                        dbc.Col(dcc.Loading(dcc.Graph(id='sunburst-graph', style={'height': '70vh'}, config={'displayModeBar': False}), color="#00bc8c"), width=12)
                    ], className="glass-card p-2")
                ], className="pt-3")
            ]),
            
            dbc.Tab(label="Corrélation Mots-clés", tab_id="tab-nlp", children=[
                html.Div([
                    dbc.Row([
                        dbc.Col(dcc.Loading(dcc.Graph(id='heatmap-graph', config={'displayModeBar': False}), color="#00bc8c"), width=12)
                    ], className="glass-card p-2")
                ], className="pt-3")
            ]),
            
            dbc.Tab(label="AI Analyst", tab_id="tab-ai", children=[
                html.Div([
                    html.H4("Assistant IA", className="mb-3"),
                    html.P("Posez une question sur le corpus...", className="text-muted"),
                    dbc.Textarea(
                        id="ai-input",
                        placeholder="Ex: Quelle est la tendance du sentiment sur la France en 2023 ?",
                        className="mb-3",
                        style={'backgroundColor': '#222', 'color': '#fff', 'border': '1px solid #444'}
                    ),
                    dbc.Button("Analyser", id="ai-submit-btn", color="success", className="mb-4"),
                    html.Div(id="ai-response-area", className="p-3 border rounded", style={'minHeight': '200px', 'backgroundColor': '#1a1a1a'})
                ], className="pt-3 glass-card p-4")
            ]),
        ],
        id="tabs-content",
        active_tab="tab-overview"
    )

def create_layout():
    return html.Div(
        [
            create_sidebar(),
            html.Div(
                [
                    create_kpi_cards(),
                    create_tabs_content(),
                    # Store for shared data signal (optional, but good practice for updates)
                    dcc.Store(id='store-data-trigger')
                ],
                className="content-area"
            )
        ]
    )
