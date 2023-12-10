import dash
from dash import html, dcc,callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from modules.webapputils import getTrends, generateCarousellTrends
import random
import re
dash.register_page(__name__, title='Página Inicial', description='Página Inicial do Perfil Público',path='/')
trends = getTrends(10)
fixed_trends=["António Costa","Ciência","Montenegro","Galamba","PSD","Ronaldo","IA","Açores","Porto","Covid","Lisboa","Benfica"]
layout_trends=list()


for t in trends :
    car,count=generateCarousellTrends(t)
    if(count>5):
        layout_trends.append(html.H2(className="topic_title",children=[t+" "]))
        layout_trends.append(car)
        layout_trends.append(html.Hr())
if(len(layout_trends)!=0):
    layout_trends=[html.H4("Tópicos relevantes atualmente e autores que escreveram sobre os mesmos:",style={"color":"black","margin-top":"2em"})]+layout_trends


layout_fixed_trends=list()
if((len(layout_trends)/3)<=5):
    #fixed_trends_sample=random.sample(fixed_trends,10-len(layout_trends))
    fixed_trends_sample=fixed_trends
    for t in fixed_trends_sample:
        car, _ = generateCarousellTrends(t)

        layout_fixed_trends.append(html.H2(t,className="topic_title"))
        layout_fixed_trends.append(car)
        #layout_fixed_trends.append(html.Hr())


layout_trends=[html.H4("Autores que escreveram sobre:",style={"color":"black"})] + layout_fixed_trends+layout_trends



row= html.Div(children=[
        dbc.Row(
            dbc.Col(
                html.Center(children=[
                    html.Br(),
                    html.P(id="output-state"),
                    html.H1(children='Perfil Público', className="display-3 title"),
                    html.Hr(className="my-4"),
                    html.P('Encontre autores adequados ao seu perfil', className="lead")
                ]),
                width={"size": 12},align="center"
            )
        ),
        dbc.Row(
            [
                dbc.Col( html.Center(children=[
                    html.Form([
                    dcc.Input(type="search", id="search-bar", placeholder="Introduza o nome de um autor", className="form-control",style={"text-align":"center"}),
                    html.Br(),

                    html.Button('Pesquisar por autor', id='submit_search_val', className="btn btn-primary submit-button",
                                n_clicks=0)
                    ],)
                    ,]),

                    width={"size": 12},
                ),


            ],align="center"
        ),
])


button_more=  dbc.Row(html.Center(dbc.Button('Procurar por Mais Tópicos', href="/recommendations", className="btn btn-primary submit-button")))

stats_group= dbc.Row([
    dbc.Col(dbc.Card(className="stats_card",children=[
                dbc.CardBody(

                            [
                                html.Center(html.H2("Mais de 88 mil artigos analisados", className="card-title")),

                                html.Center(html.P(
                                    "De diversos temas e com diferentes estruturas",
                                    className="card-text",
                                )),

                            ]
                )
        ])),
    dbc.Col(dbc.Card(className="stats_card",children=[
        dbc.CardBody(

                [
                    html.Center(html.H2("Mais de 1500 perfis automaticamente gerados", className="card-title")),

                    html.Center(html.P(
                        "De autores e jornalistas que passaram pelo jornal Público nos últimos 10 anos",
                        className="card-text",
                    )),

                ]
            )

    ])),
    dbc.Col(dbc.Card(className="stats_card",children=[
        dbc.CardBody(
            [
                html.Center(html.H2("Mais de 9800 tópicos indexados", className="card-title")),

                html.Center(html.P(
                    "Desde figuras políticas a desportistas. Desde celebridades e entidades governamentais",
                    className="card-text",
                )),

            ]
        )
    ]))


])

layout_trends=[dbc.Row(dbc.Col(children=layout_trends,className="col-md-12"))]

#layout_l = [row] + layout_trends + [button_more]+[html.Br(),html.Br()]+[stats_group]

layout_l = [row] + layout_trends +[html.Br(),html.Br()]+[stats_group]

layout=dbc.Container(fluid=True,children=layout_l)
@callback(
    Output('output-state', 'children'),
    Input('submit_search_val', 'n_clicks'),
    State('search-bar', 'value')
)
def update_output(n_clicks, input1):
    if(n_clicks):
        search =re.sub(' +', ' ', str(input1)).strip()
        if(search!=None and search!=""):
            return dcc.Location(href="/search?search="+search,id="tak")


