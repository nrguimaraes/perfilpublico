import dash
from dash import html, dcc,callback
from dash.dependencies import Input, Output
from dash_holoniq_wordcloud import DashWordcloud
import dash_daq as daq
import dash_bootstrap_components as dbc
from modules.webapputils import getPhoto
import dash_trich_components as dtc
from modules.author_recommendation import getRelatedAuthorsByMetric

import pandas as pd

dash.register_page(__name__, title="Perfil Público - Autor", description='Página de Perfil do Autor')

import modules.mongointerface as mi
import plotly.express as px

data=dict()
# http://127.0.0.1:8050/authorpage?id=640b23e071a145086170ff51


def layout(id, **other_unknown_query_strings):
	#id = "640b23e071a145086170ff51"



	return  [html.Span(id="input_id",children=id,style={"visibility":"hidden"}),dcc.Loading(id="spinner_author",type="circle"), dbc.Container(fluid=True, id="container_author")]







@callback(
    Output('wc_div', 'children'),
    Input('my-toggle-switch', 'value')
)
def update_output(value):
	global data
	wc_data = list()
	values_wc = list()
	if(value):
		entities_type = ["Organizations", "People", "Locations"]
		for ent in entities_type:
			if(data[ent]!=None):
				for k, v in data[ent].items():
					wc_data.append([k, v])
					values_wc.append(v)
	else:
		keyword_type = ["kw_1", "kw_2", "kw_3"]

		for ent in keyword_type:
			if (data[ent] != None):
				for d in data[ent]:
					wc_data.append([list(d.keys())[0], list(d.values())[0]])
					values_wc.append(list(d.values())[0])

	if(len(wc_data)!=0):
		wc_min=min(values_wc)
		wc_max=max(values_wc)
		#print(wc_data)

		for entry in wc_data:
				if(wc_min==wc_max):
					entry[1] = 100.00
				else:
					entry[1]=round((entry[1]-wc_min)/(wc_max-wc_min)*100,2)
	else:
		return ([html.H2("Nenhum valor encontrado"),html.Img(src="assets/nowc.png",width=300,height=300)])

	return(DashWordcloud(
			id='wordcloud',
			list=wc_data,
			width=700, height=400,
			gridSize=16,
			#drawOutOfBound=False,
			fontFamily="Noto Sans",
			#color='#f0f0c0',
			#backgroundColor='#001f00',
			shuffle=False,
			rotateRatio=0.5,
			shrinkToFit=True,
			shape='circle',
			hover=True
		))





@callback(
    [Output('container_author', 'children'),Output("spinner_author","style")],
	[Input("spinner_author","value"),
	   Input("input_id","children")]
)


def update_layoutAll(value,id):
	global data

	marks = dict()
	for year in range(2013, 2023):
		marks.update({year: str(year)})
	data = mi.getAuthorByID(id)

	metadata = mi.getAuthorMetadata(data["Name"])
	max_year,news_by_year = mi.getAuthorNewsCount(data["Name"])
	news_by_year_df = pd.DataFrame.from_dict(news_by_year)
	news_by_year_df.sort_values(by=["Year"], ascending=True, inplace=True)
	# cluster=buildCluster()

	fig = px.bar(x=news_by_year_df["Year"], y=news_by_year_df["Count"],
				 labels={
					 "x": "Ano",
					 "y": "Número de artigos",
				 }

				 )
	fig.update_xaxes(type='category')
	fig.update_yaxes(dtick=1)

	reading_value = data["norm_Readibility_log"] * 100
	factual_value = data["norm_EntityDiversityScore_log"] * 100
	length = data["norm_Avg_word_count_log"] * 100

	related_autors = getRelatedAuthorsByMetric(data, 20)[["id", "author"]]

	# dcc.Graph(id="cluster_authors",figure=cluster)

	profile_card = dbc.Card(dbc.Row(
		[
			dbc.Col(

				dbc.CardImg(
					src=getPhoto(data["Name"]),
					className="img-fluid rounded-start",
				),
				className="col-md-2",
			),
			dbc.Col(
				dbc.CardBody(
					[
						html.H1(data["Name"], className="card-title title"),
						html.H5(
							metadata["author_role"],
							className="card-text",
							style={"color": "grey", "font-style": "italic"}
						),
						html.P(
							metadata["newspaper"],
							className="card-text",
							style={"color": "#34495E"}
						),
						html.P(
							metadata["description"],
							className="card-text",
						),
						# html.P(
						#	"Tópicos:",
						#	className="card-text",
						# ),
						#html.Small(
						#	"Última publicação extraída a " + str(data["FirstPublication"]),
						#	className="card-text text-muted",
						#),
					]
				),
				className="col-md-4",
			),
			dbc.Col([
				html.Br(),
				html.H4("Volume de Artigos"),
				dcc.Graph(id="volume_news", figure=fig)],
				className="col-md-6",
			)
		], className="align-items-center",
	), className="g-0 d-flex")

	profile_data = dbc.Row([
		profile_card
	])

	metrics_and_wordcloud = dbc.Row([
		dbc.Col(
			[
				html.H4("Métricas de Leitura"),
				html.Br(),
				html.Br(),
				html.Div([

					html.Div(className="metric-label",
							 children=[html.Span("Fácil Leitura", style={"text-align": "left"}),
									   html.Span("Descritivo", style={"text-align": "right"})]),
					dbc.Progress([
						dbc.Progress(value=reading_value, color="#239B56", bar=True),
						dbc.Progress(value=100 - reading_value, color="#82E0AA", bar=True),
					], className="mb-3"),
					html.Div(className="metric-label", children=[html.Span("Focado", style={"text-align": "left"}),
																 html.Span("Abrangente", style={"text-align": "right"})]),
					dbc.Progress([
						dbc.Progress(value=factual_value, color="#2E86C1", bar=True),
						dbc.Progress(value=100 - factual_value, color="#85C1E9", bar=True),
					], className="mb-3"),
					html.Div(className="metric-label", children=[html.Span("Curto", style={"text-align": "left"}),
																 html.Span("Extenso", style={"text-align": "right"})]),
					dbc.Progress([
						dbc.Progress(value=length, color="#8E44AD", bar=True),
						dbc.Progress(value=100 - length, color="#D2B4DE", bar=True),
					], className="mb-3"),
				])
			],
			width={"size": 6}),
		dbc.Col(
			[
				html.H4("Palavras Chaves e Entidades Relevantes"),
				html.Br(),
				html.Center(children=[
					html.Div(id="wc_div", children=[
						html.Div(id="wc_div"),
						daq.ToggleSwitch(
							id='my-toggle-switch',
							value=False,
							size=100,
							label="Palavras-Chave|Entidades"
						)
					])
				])
			],
			width={"size": 6}, align="center"
		)
	])

	news_author = dbc.Row([
		dbc.Col(
			[html.H2("Artigos da autoria de " + data["Name"]),
			 html.Center(children=[
				 dcc.Slider(min=2013, max=2022, step=1, value=int(max_year), marks=marks, id='news_slider'),
				 dcc.Loading(id="spinner_news", type="circle", children=[html.Div(id="news_div")])

			 ])
			 ],
			width={"size": 12}, align="center"
		)
	])

	similar_author = dbc.Row([
		dbc.Col(
			[
				html.H2("Autores Semelhantes"),
				dtc.Carousel(
					[html.Div(className="carousel_div",children=[

						html.Center(html.A(children=[html.Img(src=getPhoto(row["author"]), style={"width": "161px", "height": "161px"}),row["author"]], href="/authorpage?id=" + str(row["id"])))]) for
						ind, row in related_autors.iterrows()
					],
					# slides_to_show=10,
					variable_width=True,
					infinite=False,
					arrows=False,
					center_mode=True,
					center_padding="50px"

				)
			],
			width={"size": 12}, align="center"
		)
	])
	lay=[html.Br(),
	profile_data,
	html.Br(),
	metrics_and_wordcloud,
	html.Br(),
	news_author,
	html.Br(),
	similar_author,
	html.Br(),
	html.Br()]

	prop={"visibility":"hidden"}
	return lay,prop


@callback(
    Output('news_div', 'children'),
    [Input('news_slider', 'value'),
	 Input("spinner_news","value")]
)
def update_newsTable(year,value):
	news=mi.getAuthorNewsByYear(data["Name"],year)

	table_header = [
		html.Thead(html.Tr([html.Th("Data de Extração",className="news_author_th"), html.Th("Título",className="news_author_th")],className="table-primary"))
	]





	list=[html.Tr([html.Td(r["ExtractionDate"]),html.Td(html.A(children=r["Title"], href=r["Link"],target="_blank"))])
		  for ind,r in news.iterrows()]
	table_body = [html.Tbody(list)]
	table =  html.Div(className="table-responsive", children= dbc.Table(table_header + table_body, bordered=True,id="news_author_table",className="table-striped"))

	if(len(news)==0):
		return html.Center(html.P("Nenhum resultado encontrado para o ano seleccionado"))
	return table

