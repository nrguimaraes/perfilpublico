from dash import Input, Output, State, callback, html, dcc
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from modules.chatbot_service import Chatbot_Service 
chatbot = Chatbot_Service()


def Chatbot():      

    return html.Div([
        dcc.Store(id="pending-question"),
        dcc.Store(
            id="chat-session",
            storage_type="session",
            data=[]
        ),
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
                            children=[dcc.Markdown(
                                "Olá! 👋 Sou o Assistente Perfil Público. "
                                "Posso responder a perguntas sobre autores, tópicos e artigos presentes na plataforma. "
                                "Em que posso ajudar?" )
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


@callback(
    Output("chat-history", "children", allow_duplicate=True),
    Output("chat-input", "value"),
    Output("pending-question", "data"),
    Input("send-chat", "n_clicks"),
    Input("chat-input", "n_submit"),
    State("chat-history", "children"),
    State("chat-input", "value"),
    prevent_initial_call=True,
)
def enqueue_message(_, __, history, question):

    if not question:
        raise PreventUpdate

    history.append(
        html.Div(
            html.Div(dcc.Markdown(question), className="user-bubble"),
            className="user-row"
        )
    )

    history.append(
        html.Div(
            html.Div(
                html.Div(
                    [
                        html.Span(className="thinking-dot"),
                        html.Span(className="thinking-dot"),
                        html.Span(className="thinking-dot"),
                    ],
                    className="thinking"
                ),
                className="bot-bubble"
            ),
            className="bot-row"
        )
    )

    return history, "", question


@callback(
    Output("chat-history", "children", allow_duplicate=True),
    Output("chat-session", "data"),
    Input("pending-question", "data"),
    State("chat-history", "children"),
    State("chat-session", "data"),
    State("chat-page", "children"),
    State("chat-author", "children"),
    State("chat-topic", "children"),
    prevent_initial_call=True,
)
def answer_question(question, history, session, page, author, topic):

    if session is None:
        session = []

    if not question:
        raise PreventUpdate

    answer = chatbot.ask(
        question=question,
        page=page,
        author=author,
        topic=topic,
        history=session
    )

    history.pop()

    
    history.append(
        html.Div(
            html.Div(dcc.Markdown(answer), className="bot-bubble"),
            className="bot-row"
        )
    )

    session.append({
        "role": "user",
        "content": question
    })

    session.append({
        "role": "assistant",
        "content": answer
    })

    return history, session 