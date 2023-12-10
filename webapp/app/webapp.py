# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash ,page_container,page_registry

import dash_bootstrap_components as dbc
import os

#assets_path = "./"+"app/"+"assets"
app = Dash(__name__,
           external_stylesheets=[dbc.themes.CERULEAN,'/assets/fontawesome/font-awesome.min.css'],
           use_pages=True,
           suppress_callback_exceptions=True,
#           assets_folder=assets_path
           )




navbar = dbc.NavbarSimple(class_name="title", id="navigation",  fluid=True,
    children=[
        dbc.NavItem(dbc.NavLink(page["title"], href=page["relative_path"],style={"font-size":"18px"})) for page in page_registry.values() if page['name']not in ["Authorpage","Search","Authortopicpage"]
    ],
    brand="Perfil Público",
    brand_href="/",
    color="#960b1b",
    dark=True,

)




footer= dbc.NavbarSimple(className="title", id="footer",  fluid=True,

    #brand="Perfil Público",
    #brand_href="/",
    color="#d00018",
    dark=True,

)

app.layout = dbc.Container(fluid=True,children=[
    navbar,
    page_container,
    #footer
])


server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8050", debug=False)

