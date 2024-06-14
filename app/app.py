"""Módulo principal da aplicação Dash."""

import dash
import dash_bootstrap_components as dbc

SCRIPTS = [
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/locale/pt-br.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/locale/de.min.js",
]

ESTILOS = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://fonts.googleapis.com/icon?family=Material+Icons",
    dbc.themes.BOOTSTRAP,
]

DBC_CSS = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

MANTINE_STYLESHEETS = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]

# pylint: disable=W0212
# Configuração do React
dash._dash_renderer._set_react_version("18.2.0")

app = dash.Dash(
    __name__,
    external_stylesheets=ESTILOS + [DBC_CSS] + MANTINE_STYLESHEETS,
    external_scripts=SCRIPTS,
)

app.config.suppress_callback_exceptions = True
app.title = "Shop Floor Management - Automação"
app.scripts.config.serve_locally = True
server = app.server

# Configuração do layout para PT-BR
app.index_string = """
<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
