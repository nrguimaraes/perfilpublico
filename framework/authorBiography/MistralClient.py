import os

from mistralai.client import Mistral

class MistralClient:

    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            raise ValueError("MISTRAL_API_KEY not configured")

        self.client = Mistral(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content.strip()