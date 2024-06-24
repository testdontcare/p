import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pycountry
import dash_bootstrap_components as dbc

df = pd.read_csv('universal_top_spotify_songs.csv')

df['snapshot_date'] = pd.to_datetime(df['snapshot_date'])
df['country'] = df['country'].fillna('Все страны')

def convert_country(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code

df['country_names'] = df['country'].apply(convert_country)
country_options = [{'label': country, 'value': country} for country in sorted(df['country_names'].unique()) if country != 'Все страны']
country_options.insert(0, {'label': 'Все страны', 'value': 'Все страны'})

def render_main_page():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.DatePickerSingle(
                    id='date-picker',
                    min_date_allowed=df['snapshot_date'].min(),
                    max_date_allowed=df['snapshot_date'].max(),
                    initial_visible_month=df['snapshot_date'].min(),
                    date=df['snapshot_date'].max(),
                    style={'height': '50px'}
                )
            ], width=6),
            dbc.Col([
                dcc.Dropdown(
                    id='country-dropdown',
                    options=country_options,
                    value='Все страны',
                    clearable=False,
                    style={'flex': '1', 'height': '50px'}
                )
            ], width=6)
        ], style={'margin-bottom': '20px'}),
        
        dbc.Row([
            dbc.Col([
                html.H3('По ранкингу'),
                html.Div(id='top-songs-ranking')
            ], width=6),
            dbc.Col([
                dcc.Graph(id='country-map', config={'scrollZoom': False}),
                html.Div(id='artist-with-most-songs', style={'margin-top': '20px'})
            ], width=6)
        ], style={'margin-bottom': '5px'}),

        dbc.Row([
            dbc.Col([
                html.H3('По популярности'),
                dcc.Graph(id='top-songs-popularity', style={'width': '100%', 'margin': '0 auto'})
            ], width=6),
            dbc.Col([
                html.H3('Новинки в чарте'),
                dcc.Dropdown(
                    id='movement-dropdown', 
                    options=[
                        {'label': 'Дневные изменения', 'value': 'daily_movement'},
                        {'label': 'Недельные изменения', 'value': 'weekly_movement'}
                    ], 
                    value='daily_movement',
                    style={'margin-bottom': '20px', 'width': '100%'}
                ),
                dcc.Graph(id='top-movement-songs', style={'width': '100%'})
            ], width=6)
        ], style={'margin-bottom': '20px'}),
        
        dbc.Row([
            dbc.Col([
                html.H3('Лидирующий артист'),
                html.Div(id='artist-with-most-songs')
            ], width=6),
            dbc.Col([
                html.H3('Откровенное содержание'),
                html.Div(id='explicit-content-text')
            ], width=6)
        ], style={'margin-bottom': '20px'}),
        
        dbc.Row([
            html.H3('Средние значения топ 50'),
            html.Div(id='average-values', style={'width': '100%'})
        ], style={'margin-bottom': '20px'})
    ], style={'font-family': 'Arial, sans-serif'})

def register_callbacks(app):
    @app.callback(
        Output('country-map', 'figure'),
        [Input('date-picker', 'date'), Input('country-dropdown', 'value')]
    )
    def update_map(selected_date, selected_country):
        filtered_df = df[df['snapshot_date'] == selected_date]

        fig = px.choropleth(
            filtered_df,
            locations='country_names',
            locationmode='country names',
            hover_name='name',
        )

        fig.update_layout(
            geo=dict(
                showcountries=True,
                showframe=False,
                showcoastlines=False,
                projection_type='natural earth',
                showlakes=False
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            hovermode=False,
            width=700,
            height=300
        )
        fig.update_traces(
            hoverinfo='none',
            selector=dict(type='choropleth')
        )

        if selected_country != 'Все страны':
            fig.add_trace(go.Choropleth(
                locations=[selected_country],
                z=[1],
                locationmode='country names',
                colorscale=[[0, 'lawngreen'], [1, 'lawngreen']],
                showscale=False,
                marker_line_width=2
            ))

        return fig

    @app.callback(
        Output('top-songs-ranking', 'children'),
        [Input('date-picker', 'date'), Input('country-dropdown', 'value')]
    )
    def update_top_songs_ranking(selected_date, selected_country):
        country = selected_country if selected_country else 'Все страны'
        filtered_df = df[(df['snapshot_date'] == selected_date) & (df['country_names'] == country)].sort_values(by='daily_rank').head(5)
        return html.Div([
            html.Div([
                html.Div(f"{row['daily_rank']}. {row['name']} - {row['artists']}", style={'margin-bottom': '1px', 'font-weight': 'bold'}),
                html.Div([
                    html.Img(src='/assets/danceability_small.png', style={'height': '20px', 'margin-right': '5px'}),
                    html.Span(f"{row['danceability']}"),
                    html.Img(src='/assets/energy_small.png', style={'height': '20px', 'margin-left': '10px', 'margin-right': '5px'}),
                    html.Span(f"{row['energy']}"),
                    html.Img(src='/assets/acousticness_small.png', style={'height': '20px', 'margin-left': '10px', 'margin-right': '5px'}),
                    html.Span(f"{row['acousticness']}"),
                    html.Img(src='/assets/valence_small.png', style={'height': '20px', 'margin-left': '10px', 'margin-right': '5px'}),
                    html.Span(f"{row['valence']}"),
                    html.Img(src='/assets/tempo_small.png', style={'height': '20px', 'margin-left': '10px', 'margin-right': '5px'}),
                    html.Span(f"{row['tempo']:.0f} BPM"),
                    html.Img(src='/assets/loudness_small.png', style={'height': '20px', 'margin-left': '10px', 'margin-right': '5px'}),
                    html.Span(f"{row['loudness']} дБ")
                ], style={'font-size': '0.8em'})
            ])
            for i, row in filtered_df.iterrows()
        ])

    @app.callback(
        Output('top-songs-popularity', 'figure'),
        [Input('date-picker', 'date'), Input('country-dropdown', 'value')]
    )
    def update_top_songs_popularity(selected_date, selected_country):
        country = selected_country if selected_country else 'Все страны'
        filtered_df = df[(df['snapshot_date'] == selected_date) & (df['country_names'] == country)].sort_values(by='popularity', ascending=False).head(5)
        fig = px.bar(filtered_df, x='name', y='popularity', color='artists', text='popularity')
        fig.update_layout(
            showlegend=False,
            yaxis=dict(showticklabels=True, range=[0, 100]),
            yaxis_title=None,
            xaxis_title=None,
            margin=dict(l=20, r=20, t=20, b=20),
            height=400
        )
        fig.update_traces(width=0.5, texttemplate='%{text:.2s}', textposition='outside')
        fig.update_xaxes(tickangle=0, tickvals=filtered_df['name'], ticktext=[(text[:20] + '...') if len(text) > 20 else text for text in filtered_df['name']])
        return fig

    @app.callback(
        Output('top-movement-songs', 'figure'),
        [Input('date-picker', 'date'), Input('movement-dropdown', 'value'), Input('country-dropdown', 'value')]
    )
    def update_top_movement_songs(selected_date, movement_type, selected_country):
        country = selected_country if selected_country else 'Все страны'
        filtered_df = df[(df['snapshot_date'] == selected_date) & (df['country_names'] == country)].sort_values(by=movement_type, ascending=False).head(5)
        fig = px.bar(filtered_df, x='name', y=movement_type, color='artists', text=movement_type)
        fig.update_layout(
            showlegend=False,
            yaxis=dict(showticklabels=True),
            yaxis_title=None,
            xaxis_title=None,
            margin=dict(l=20, r=20, t=20, b=20),
            height=344
        )
        fig.update_traces(width=0.5, texttemplate='%{text:.2s}', textposition='outside')
        fig.update_xaxes(tickangle=0, tickvals=filtered_df['name'], ticktext=[(text[:20] + '...') if len(text) > 20 else text for text in filtered_df['name']])
        return fig

    @app.callback(
        Output('artist-with-most-songs', 'children'),
        [Input('date-picker', 'date'), Input('country-dropdown', 'value')]
    )
    def update_artist_with_most_songs(selected_date, selected_country):
        country = selected_country if selected_country else 'Все страны'
        filtered_df = df[(df['snapshot_date'] == selected_date) & (df['country_names'] == country)]
    
        if filtered_df.empty:
            return "-"

        most_songs_artist = filtered_df['artists'].mode().values[0]
        song_count = filtered_df['artists'].value_counts().max()
        return f"{most_songs_artist} ({song_count} песен)"

    @app.callback(
        Output('explicit-content-text', 'children'),
        [Input('date-picker', 'date'), Input('country-dropdown', 'value')]
    )
    def update_explicit_content_text(selected_date, selected_country):
        country = selected_country if selected_country else 'Все страны'
        filtered_df = df[(df['snapshot_date'] == selected_date) & (df['country_names'] == country)]
        explicit_count = filtered_df['is_explicit'].value_counts()
        total_songs = explicit_count.sum()
        explicit_percentage = (explicit_count.get(True, 0) / total_songs * 100) if total_songs > 0 else 0
        return f"{explicit_percentage:.0f}% песен имеют откровенное содержание"

    @app.callback(
        Output('average-values', 'children'),
        [Input('date-picker', 'date'), Input('country-dropdown', 'value')]
    )
    def update_average_values(selected_date, selected_country):
        country = selected_country if selected_country else 'Все страны'
        filtered_df = df[(df['snapshot_date'] == selected_date) & (df['country_names'] == country)]
        avg_values = filtered_df[['danceability', 'energy', 'acousticness', 'valence', 'tempo', 'loudness']].mean()
        
        avg_value_labels = ['Danceability', 'Energy', 'Acousticness', 'Valence', 'Tempo', 'Loudness']
        avg_value_icons = ['danceability.png', 'energy.png', 'acousticness.png', 'valence.png', 'tempo.png', 'loudness.png']
        avg_value_texts = [
            f"{avg_values['danceability']:.2f}",
            f"{avg_values['energy']:.2f}",
            f"{avg_values['acousticness']:.2f}",
            f"{avg_values['valence']:.2f}",
            f"{avg_values['tempo']:.0f} BPM",
            f"{avg_values['loudness']:.2f} дБ"
        ]

        return html.Div([
            html.Div([
                html.Img(src=f'/assets/{icon}', style={'height': '80px'}),
                html.Div(text)
            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
            for icon, text in zip(avg_value_icons, avg_value_texts)
        ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '12px', 'font-family': 'Arial, sans-serif'})

register_callbacks(dash.Dash(__name__))
