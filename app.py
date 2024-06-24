import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from main_page import render_main_page, register_callbacks as register_main_callbacks
from map_page import render_map_page, register_callbacks as register_map_callbacks
from about_page import render_about_page

app = dash.Dash(__name__,suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.LITERA])

def generate_navbar(pathname):
    if pathname == '/map':
        nav_items = [
            dbc.NavItem(dbc.NavLink("Отчет по стране за дату", href="/")),
            dbc.NavItem(dbc.NavLink("О проекте", href="/about"))
        ]
    elif pathname == '/about':
        nav_items = [
            dbc.NavItem(dbc.NavLink("Отчет по стране за дату", href="/")),
            dbc.NavItem(dbc.NavLink("Общий отчет за период", href="/map"))
        ]
    else:
        nav_items = [
            dbc.NavItem(dbc.NavLink("Общий отчет за период", href="/map")),
            dbc.NavItem(dbc.NavLink("О проекте", href="/about"))
        ]
    return dbc.NavbarSimple(
        children=nav_items,
        brand="Дашборд Воробьева Е.К.",
        dark=True,
        fixed="top",
        color="success"
    )

app.layout = html.Div(style={'backgroundColor': '#FFFFFF', 'color': '#000000'}, children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar'),
    html.Div(id='page-content', style={'paddingTop': '4rem'})
])

@app.callback(Output('page-content', 'children'),
              Output('navbar', 'children'),
              Input('url', 'pathname'))
def render_page_content(pathname):
    navbar = generate_navbar(pathname)
    if pathname == '/map':
        return render_map_page(), navbar
    elif pathname == '/about':
        return render_about_page(), navbar
    else:
        return render_main_page(), navbar

register_main_callbacks(app)
register_map_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
