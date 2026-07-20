import os
from mistralai.client import Mistral

from modules.chromainterface import get_similar_authors


class MistralClient:

    def __init__(self):
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    def embed(self, text: str):
        response = self.client.embeddings.create(
            model="mistral-embed",
            inputs=[text],
        )

        return response.data[0].embedding
    
  