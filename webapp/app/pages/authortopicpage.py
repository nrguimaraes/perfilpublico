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

dash.register_page(__name__, title="Perfil Público - Autor x Tópico", description='Página de Perfil do Autor x Tópico')

import modules.mongointerface as mi
import plotly.express as px

data=dict()
# http://127.0.0.1:8050/authorpage?id=640b23e071a145086170ff51


def layout(id, topic, **other_unknown_query_strings):
	#id = "640b23e071a145086170ff51"



	return  [html.Span(id="topic_input_id",children=id,style={"visibility":"hidden"}),
			 html.Span(id="topic_name", children=topic, style={"visibility": "hidden"}),
			 dcc.Loading(id="topic_spinner_author",type="circle"), dbc.Container(fluid=True, id="topic_container_author")]












@callback(
    [Output('topic_container_author', 'children'),Output("topic_spinner_author","style")],
	[	Input("topic_spinner_author","value"),
		Input("topic_input_id","children"),
	   	Input("topic_name", "children")]
)


def update_layoutAll(value,id,topic):
	global data

	marks = dict()
	for year in range(2013, 2023):
		marks.update({year: str(year)})
	data = mi.getAuthorByID(id)



	"""
	PLOT COUNT
	"""

	metadata = mi.getAuthorMetadata(data["Name"])


	max_year,news_by_year = mi.getAuthorNewsCount(data["Name"])
	news_by_year_df = pd.DataFrame.from_dict(news_by_year)
	news_by_year_df["type"]="todos"

	max_topic_year,news_by_topic = mi.getAuthorTopicNewsCount(data["Name"],topic)
	news_by_topic_df = pd.DataFrame.from_dict(news_by_topic)
	news_by_topic_df["type"]=topic

	news_by_year_df=pd.concat([news_by_year_df,news_by_topic_df])
	news_by_year_df.sort_values(by=["Year"], ascending=True, inplace=True)

	fig = px.bar(x=news_by_year_df["Year"], y=news_by_year_df["Count"], color=news_by_year_df["type"], barmode='group',
				 labels={
					 "x": "Ano",
					 "y": "Número de artigos",
				 }

				 )
	fig.update_xaxes(type='category')
	fig.update_yaxes(dtick=1)


	"""
	READING
	"""

	reading_value = data["norm_Readibility_log"] * 100
	factual_value = data["norm_EntityDiversityScore_log"] * 100
	length = data["norm_Avg_word_count_log"] * 100

	related_autors = getRelatedAuthorsByMetric(data, 20)[["id", "author"]]

	# dcc.Graph(id="cluster_authors",figure=cluster)

	profile_card = dbc.Card(dbc.Row(
		[
			dbc.Col([

				dbc.CardImg(
					src=getPhoto(data["Name"]),
					className="img-fluid rounded-start",
				),

				html.Center(dbc.Button('Consultar Perfil', href="/authorpage?id=" + id,
									   className="btn btn-primary submit-button", style={"margin-top":"0.5em"}))
				],

				className="col-md-2",
			),
			dbc.Col(
				[dbc.CardBody(
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
				)]
				,
				className="col-md-4",
			),
			dbc.Col([
				html.Br(),
				html.H4("Volume de Artigos"),
				html.H5("Todos vs "+topic,style={"color":"black"}),
				dcc.Graph(id="topic_volume_news", figure=fig)],
				className="col-md-6",
			)
		], className="align-items-center",
	), className="g-0 d-flex")

	profile_data = dbc.Row([
		profile_card
	])


	news_author = dbc.Row([
		dbc.Col(
			[html.H2("Artigos de " + data["Name"] + " sobre " +topic),
			 #html.H5("Sobre o tópico "+topic, style={"color":"black"}),
			 html.Center(children=[
				 dcc.Slider(min=2013, max=2022, step=1, value=int(max_topic_year), marks=marks, id='topic_news_slider'),
				 dcc.Loading(id="topic_spinner_news", type="circle", children=[html.Div(id="topic_news_div")])

			 ])
			 ],
			width={"size": 12}, align="center"
		)
	])


	lay=[html.Br(),
	profile_data,
	html.Br(),
	news_author,
	html.Br()]

	prop={"visibility":"hidden"}
	return lay,prop


@callback(
    Output('topic_news_div', 'children'),
    [Input('topic_news_slider', 'value'),
	Input("topic_name", "children"),
	 Input("topic_spinner_news","value")]
)
def update_newsTable(year,topic,value):
	news=mi.getAuthorNewsByYearAndTopic(data["Name"],year,topic)

	table_header = [
		html.Thead(html.Tr([html.Th("Data de Extração",className="news_author_th"), html.Th("Título",className="news_author_th")],className="table-primary"))
	]

	list=[html.Tr([html.Td(r["ExtractionDate"]),html.Td(html.A(children=r["Title"], href=r["Link"],target="_blank"))])
		  for ind,r in news.iterrows()]
	table_body = [html.Tbody(list)]
	table =  html.Div(className="table-responsive", children= dbc.Table(table_header + table_body, bordered=True,id="topic_news_author_table",className="table-striped"))

	if(len(news)==0):
		return html.Center(html.P("Nenhum resultado encontrado para o ano seleccionado"))
	return table

