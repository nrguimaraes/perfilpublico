from modules.chattools import ChatTools
from modules.mistralclient import MistralClient
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate

from modules.contextformatter import ContextFormatter

prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
    És o Assistente do Perfil Público.

    Responde sempre em português europeu.

    Utiliza apenas a informação presente no contexto.

    O contexto corresponde a TODOS os resultados encontrados na base de dados.

    Se o utilizador perguntar:
    - "quantos", utiliza o número de resultados indicado no contexto;
    - "quais", enumera os artigos presentes;
    - "sobre o que escreve", resume os temas presentes.

    Nunca inventes informação.

    Contexto:

    {context}
    """
        ),

        ("placeholder", "{history}"),

        ("human", "{question}")
])

class Chatbot_Service:

    def __init__(self):
        self.tools = ChatTools()
        self.mistral = MistralClient()
        self.history = InMemoryChatMessageHistory()

    def ask(self, question, page, author=None, topic=None):

        intent = self.mistral.classify_intent(
            question=question,
            page=page
        )

        context = self.tools.execute(
            intent=intent,
            question=question,
            author=author,
            topic=topic
        )
        print(context)
        formatted_context = ContextFormatter.format(context)

    
        messages = prompt.invoke({
            "context": formatted_context,
            "history": self.history.messages,
            "question": question
        }).to_messages()

        

        answer = self.mistral.generate(messages)

        self.history.add_user_message(question)
        self.history.add_ai_message(answer)

        return answer