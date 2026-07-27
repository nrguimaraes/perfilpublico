from dash import Input, Output, callback, html, dcc
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

chatbot     = html.Div([

    html.Button(
        html.Img(
            src="/assets/chat.png",
            className="chat-icon"
        ),
        id="open-chat",
        className="chat-button"
    ),

    dbc.Offcanvas(
        id="chat-panel",
        placement="end",
        title="Assistente Perfil Público",
        className="chat-panel",
        backdrop=False,
        scrollable=True,
        children=[
            html.Div(
                id="chat-history",
                className="chat-history",
                children=[
                    html.Div(
                        className="bot-message",
                        children=[
                            "Olá! 👋 Sou o Assistente Perfil Público. "
                            "Posso responder a perguntas sobre autores, tópicos e artigos presentes na plataforma. "
                            "Em que posso ajudar?"
                        ]
                    )
                ]
            ),

            html.Div(
                className="chat-input-area",
                children=[
                    dcc.Input(
                        id="chat-input",
                        className="chat-input",
                        placeholder="Escreva uma pergunta..."
                    ),

                    html.Button(
                        html.Img(src="/assets/send.png",
                                className="send-icon"),
                        id="send-chat",
                        className="send-button",
                    )
                ]
            )
        ]
    )
])

@callback(
    Output("chat-panel", "is_open"),
    Output("open-chat", "style"),
    Input("open-chat", "n_clicks"),
    Input("chat-panel", "is_open"),
    prevent_initial_call=True,
)
def toggle_chat(open_clicks, is_open):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "open-chat":
        return True, {"display": "none"}

    if not is_open:
        return False, {"display": "block"}

    return dash.no_update, {"display": "none"}