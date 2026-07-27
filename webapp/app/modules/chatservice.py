from modules.mistralclient import MistralClient
from modules.chattools import ChatTools

class ChatService:

    def __init__(self):

        self.mistral = MistralClient()
        self.tools = ChatTools()

    def answer(self, question, page, author=None, topic=None):

        intent = self.mistral.classify_intent(question, page)

        context = self.tools.execute(intent, question, author, topic)

        return context