"""Módulo principal da aplicação Dash."""
import dash
import dash_bootstrap_components as dbc

ESTILOS = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://fonts.googleapis.com/icon?family=Material+Icons",
    dbc.themes.BOOTSTRAP,
]
DBC_CSS = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=ESTILOS + [DBC_CSS])

app.config.suppress_callback_exceptions = True
app.title = "Shop Floor Management - Automação"
app.scripts.config.serve_locally = True
server = app.server
