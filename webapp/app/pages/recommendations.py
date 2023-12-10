import dash
from dash import html, dcc,callback
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
from modules.webapputils import getPhoto
dash.register_page(__name__,title='Pesquisa Avançada', description='Pesquisa Avançada Perfil Público')
import modules.mongointerface as mi

def layout():


		return dbc.Container(
			children=[
                dbc.Row([
                    html.Br(),
                    html.H1(children='Pesquisa Avançada'),
                    html.Br(),
                    dcc.Tabs([
                        dcc.Tab(label='Por Métricas', children=[
                            html.H2(children='Por Métricas'),
                            html.Br(),
                            html.Div(id="metrics_div",children=[
                                html.Div(className="metric-label",
                                         children=[html.Span("Fácil Leitura", style={"text-align": "left"}),
                                                   html.Span("Descritivo", style={"text-align": "right"})]),
                                dcc.RangeSlider(0, 100, value=[0, 20],id="readability-slider"),
                                html.Br(),
                                html.Div(className="metric-label",
                                         children=[html.Span("Focado", style={"text-align": "left"}),
                                                   html.Span("Abrangente", style={"text-align": "right"})]),
                                dcc.RangeSlider(0, 100, value=[0, 20], id="factual-slider"),
                                html.Br(),
                                html.Div(className="metric-label", children=[html.Span("Curto", style={"text-align": "left"}),
                                                                             html.Span("Extenso",
                                                                                       style={"text-align": "right"})]),
                                dcc.RangeSlider(0, 100, value=[0, 20], id="length-slider"),
                                html.Br(),
                                ]),
                                html.Br(),

                                dbc.Row(id="result_search", children=[

                                ]),
                            ]),
                        dcc.Tab(label='Por Tópico', children=[
                            html.H2("Por Tópico"),
                            html.Br(),
                            dbc.Row(
                                [
                                    dbc.Col(html.Center(children=[

                                            dcc.Input(type="search", id="search_bar_topic", className="form-control"),
                                            html.Br(),

                                            html.Button('Pesquisar Tópico', id='submit_val_topic',
                                                        className="btn btn-primary submit-button",
                                                        n_clicks=0)

                                        , ]),

                                        width={"size": 12},
                                    ),

                                ], align="center"
                            ),
                            dbc.Row(id="result_search_topic", children=[


                            ]),

                        ])
                    ])
                ]),




				]
			,fluid=True)
@callback(
    Output('result_search', 'children'),
    Input('readability-slider', 'value'),
    Input('factual-slider', 'value'),
    Input('length-slider', 'value')
)
def update_output(read_range,factual_range,length_range):
    result=mi.getRecommendationAuthors(read_range,factual_range,length_range)
    list_of_cards=list()
    for id, name in result:
        photo = getPhoto(name)
        card = dbc.Col(
            dbc.Card([
                dbc.CardBody(html.P(children=[html.A(children=name, href="/authorpage?id=" + str(id))],
                                    className="card-text")),
                dbc.CardImg(src=photo, bottom=True, class_name="pb-3"),
            ],
                color="primary",
                outline=True, className="h-100",
                class_name="mt-3 mb-3"

            ),
            className="col-12 col-sm-12 col-md-2 col-lg-2"
        )
        list_of_cards.append(card)





    #html.Div(html.Img(src="assets/user.png")),
    return list_of_cards


@callback(
    Output('result_search_topic', 'children'),
    Input('submit_val_topic', 'n_clicks'),
    State('search_bar_topic', 'value')
)



def updateResultsTopic(n_clicks,search):
    if(n_clicks):

        result=mi.searchSimilarTopics(search)
        list_of_cards =list()
        list_of_cards.append(html.H4("Autores que escreveram sobre o tópico " +search,style={"color":"black"} ))
        for item in result:
            photo = getPhoto(item["author_name"])
            card = dbc.Col(
                dbc.Card([
                    dbc.CardBody(html.P(children=[html.A(children=item["author_name"],
                                                         href="/authortopicpage?id=" + str(item["author_id"])+"&topic="+item["topic"]
                                                         )],
                                        className="card-text")),
                    dbc.CardImg(src=photo, bottom=True, class_name="pb-3")
                    #dbc.CardFooter("Tópico encontrado: " + item["topic"] ),
                ],
                    color="primary",
                    outline=True, className="h-100",
                    class_name="mt-3 mb-3"

                ),
                className="col-12 col-sm-12 col-md-2 col-lg-2"
            )
            list_of_cards.append(card)





        #html.Div(html.Img(src="assets/user.png")),
        return list_of_cards

