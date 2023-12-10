import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import modules.mongointerface as mi
from modules.webapputils import getPhoto
dash.register_page(__name__)


def layout(search=None, **other_unknown_query_strings):


	results=mi.searchAuthor(search)


	if type(results)==dict:
		return dcc.Location(href="/authorpage?id=" + str(str(results["_id"])), id="tak")

	if(type(results)==list and len(results)>0):

		list_of_cards=list()
		for r in results:
			photo=getPhoto(r["Name"])
			card=dbc.Col(
					dbc.Card([
							dbc.CardBody(html.P(children=[html.A(children=r["Name"],href="/authorpage?id="+str(r["_id"]))], className="card-text")),
							dbc.CardImg(src=photo, bottom=True,class_name="pb-3"),
						],
						color="primary",
						outline=True,className="h-100",
						class_name="mt-3 mb-3"


					),
				className="col-12 col-sm-12 col-md-2 col-lg-2"
				)
			list_of_cards.append(card)





		cards = dbc.Container([
			html.Br(),
			dbc.Row(html.H1("Resultados da Pesquisa: " + search)),
			html.Br(),
			dbc.Row(list_of_cards)],

			fluid=True)
		return cards







	notfound = dbc.Container([
		html.Br(),
		dbc.Row(html.H1("Nenhum encontrado para a pesquisa: " + search )),
		html.Br(),
		dbc.Row(html.H3(html.A(children="Voltar ao Início",href="/"))),
		html.Br(),
		html.Br(),
		dbc.Row(html.Center(html.Img(src="assets/notfound.jpg",style={"max-width":"800px"})))],

		fluid=True)
	return  notfound