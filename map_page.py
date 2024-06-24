import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pycountry

df = pd.read_csv('universal_top_spotify_songs.csv')
df['snapshot_date'] = pd.to_datetime(df['snapshot_date'])
df['tempo'] = df['tempo'].round()

def convert_country(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code

df['country_names'] = df['country'].apply(convert_country)

def render_map_page():
    return html.Div([
        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date='2024-06-17',
                end_date='2024-06-20',
                display_format='DD.MM.YY'
            ),
            dcc.Dropdown(
                id='value-dropdown',
                options=[
                    {'label': 'Танцевальность', 'value': 'danceability'},
                    {'label': 'Энергичность', 'value': 'energy'},
                    {'label': 'Акустичность', 'value': 'acousticness'},
                    {'label': 'Валентность', 'value': 'valence'},
                    {'label': 'Темп', 'value': 'tempo'},
                    {'label': 'Громкость', 'value': 'loudness'}
                ],
                value='danceability',
                style={'flex': '1'}
            ),
        ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px', 'width': '750px'}),
        html.Div([dcc.Graph(id='map')])
    ])

def register_callbacks(app):
    @app.callback(
        Output('map', 'figure'),
        [Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('value-dropdown', 'value')]
    )
    def update_map(start_date, end_date, selected_value):
        filtered_df = df[(df['snapshot_date'] >= start_date) & (df['snapshot_date'] <= end_date)]
        avg_values = filtered_df.groupby('country_names')[selected_value].mean().reset_index()
        
        fig = px.choropleth(
            avg_values,
            locations='country_names',
            locationmode='country names',
            color=selected_value,
            hover_name='country_names',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        return fig

register_callbacks(dash.Dash(__name__))
