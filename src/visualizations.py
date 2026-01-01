import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .data_processing import explode_entities, compute_cooccurrence_matrix

TEMPLATE = "plotly_dark"
COLOR_SCALE = "Teal"

def create_timeline(df):
    """
    Creates a time series chart of article volume with a RangeSlider.
    """
    if df.empty:
        return go.Figure()
        
    # Resample by day
    daily_counts = df.groupby(df['date'].dt.date).size().reset_index(name='count')
    
    fig = px.area(daily_counts, x='date', y='count', 
                  title="Évolution du Volume d'Articles",
                  template=TEMPLATE)
    
    fig.update_traces(line_color='#00bc8c', fillcolor='rgba(0, 188, 140, 0.3)')
    
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor="#222",
                activecolor="#00bc8c",
                font=dict(color="white")
            ),
            rangeslider=dict(visible=True, bordercolor="#444", bgcolor="#111"),
            type="date",
            gridcolor="rgba(255,255,255,0.1)"
        ),
        yaxis=dict(
            title="Nombre d'articles",
            gridcolor="rgba(255,255,255,0.1)"
        ),
        title_font_size=16,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Inter, sans-serif", color='#e0e0e0')
    )
    return fig

def create_sunburst(df):
    """
    Creates a Sunburst chart: Monde -> Locations -> Organizations (Top 50).
    Using a proxy logic to link Locations with Organizations present in the same articles.
    """
    if df.empty:
        return go.Figure()

    # Strategy: Explode both Loc and Org. 
    # This can be expensive. Let's simplify: Take top pairs.
    # We create a list of (Loc, Org) tuples from each article.
    
    pairs = []
    # Limit to first few items to keep it readable and performant
    for _, row in df.iterrows():
        locs = row['loc'][:2] if len(row['loc']) > 0 else ['Unknown Loc']
        orgs = row['org'][:2] if len(row['org']) > 0 else ['Unknown Org']
        for l in locs:
            for o in orgs:
                pairs.append({'World': 'Monde', 'Location': l, 'Organization': o})
                
    flat_df = pd.DataFrame(pairs)
    
    # Filter to top occurrences to avoid clutter
    if len(flat_df) > 1000:
        top_locs = flat_df['Location'].value_counts().head(20).index
        flat_df = flat_df[flat_df['Location'].isin(top_locs)]
    
    grouped = flat_df.groupby(['World', 'Location', 'Organization']).size().reset_index(name='count')
    
    fig = px.sunburst(grouped, path=['World', 'Location', 'Organization'], values='count',
                      color='count', color_continuous_scale=COLOR_SCALE,
                      title="Hiérarchie Lieux - Organisations",
                      template=TEMPLATE)
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        title_font_size=16,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color='#e0e0e0')
    )
    return fig

def create_cooccurrence_heatmap(df):
    """
    Creates a heatmap of keyword co-occurrences.
    """
    if df.empty:
        return go.Figure()
        
    cooc_mat = compute_cooccurrence_matrix(df, entity_col='kws', top_n=25)
    
    fig = go.Figure(data=go.Heatmap(
        z=cooc_mat.values,
        x=cooc_mat.columns,
        y=cooc_mat.index,
        colorscale='Viridis',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Matrice de Co-occurrence des Mots-clés",
        template=TEMPLATE,
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color='#e0e0e0'),
        xaxis=dict(side="bottom", tickangle=-45)
    )
    return fig

def create_top_persons_bar(df):
    """
    Creates a horizontal bar chart for the top 20 cited persons.
    """
    if df.empty:
        return go.Figure()

    all_persons = explode_entities(df, 'per')
    top_persons = all_persons.value_counts().head(20).reset_index()
    top_persons.columns = ['Person', 'Count']
    top_persons = top_persons.sort_values(by='Count', ascending=True) # Ascending for horiz bar
    
    fig = px.bar(top_persons, x='Count', y='Person', orientation='h',
                 title="Top 20 Personnalités Citées",
                 template=TEMPLATE,
                 color='Count', color_continuous_scale=COLOR_SCALE)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Mentions",
        yaxis_title="",
        font=dict(family="Inter, sans-serif", color='#e0e0e0'),
        coloraxis_showscale=False
    )
    return fig

def create_top_locations_bar(df):
    """
    Creates a horizontal bar chart for the top 15 cited locations.
    """
    if df.empty:
        return go.Figure()

    all_locs = explode_entities(df, 'loc')
    top_locs = all_locs.value_counts().head(15).reset_index()
    top_locs.columns = ['Location', 'Count']
    top_locs = top_locs.sort_values(by='Count', ascending=True)
    
    fig = px.bar(top_locs, x='Count', y='Location', orientation='h',
                 title="Top 15 Lieux Mentionnés",
                 template=TEMPLATE,
                 color='Count', color_continuous_scale='Purples')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Mentions",
        yaxis_title="",
        font=dict(family="Inter, sans-serif", color='#e0e0e0'),
        coloraxis_showscale=False
    )
    return fig

def create_wordcloud_scatter(df):
    """
    Creates a word cloud-like scatter plot using Plotly.
    Words are sized by frequency.
    """
    if df.empty:
        return go.Figure()
    
    all_kws = explode_entities(df, 'kws')
    kw_counts = all_kws.value_counts().head(50)
    
    if kw_counts.empty:
        return go.Figure()
    
    # Normalize sizes
    max_count = kw_counts.max()
    min_size, max_size = 12, 60
    sizes = min_size + (kw_counts / max_count) * (max_size - min_size)
    
    # Create random positions
    import random
    random.seed(42)
    x_pos = [random.uniform(0, 100) for _ in range(len(kw_counts))]
    y_pos = [random.uniform(0, 100) for _ in range(len(kw_counts))]
    
    fig = go.Figure()
    
    for i, (word, count) in enumerate(kw_counts.items()):
        fig.add_trace(go.Scatter(
            x=[x_pos[i]],
            y=[y_pos[i]],
            mode='text',
            text=[word],
            textfont=dict(size=sizes.iloc[i], color='#00bc8c'),
            hoverinfo='text',
            hovertext=f"{word}: {count} mentions",
            showlegend=False
        ))
    
    fig.update_layout(
        title="Nuage de Mots-clés",
        template=TEMPLATE,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        font=dict(family="Inter, sans-serif", color='#e0e0e0'),
        height=400
    )
    return fig
