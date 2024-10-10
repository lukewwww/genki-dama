
import json
import os
import requests
from genki.model_evaluator.api.api import GPTAPI
from PIL import Image
import base64
from io import BytesIO

ENDPOINT = 'https://api.anthropic.com/v1/messages'


class ClaudeAPI(GPTAPI):

    def __init__(self) -> None:
        super().__init__()
        if not os.getenv("CLAUDE_API_ACCESS_TOKEN"):
            raise ValueError("No Claude API access token found.")
        self.api_key = os.getenv("CLAUDE_API_ACCESS_TOKEN")

        if not os.getenv("CLAUDE_ENDPOINT"):
            self.api_endpoint=ENDPOINT
        else:
            self.api_endpoint=os.getenv("CLAUDE_ENDPOINT")


    def get_response_from_text(self, text: str) -> str:

        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json',
        }

        data = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": text}
            ]
        }

        response = requests.post(self.api_endpoint, headers=headers, data=json.dumps(data))
        response_json = response.json()

        response_text = ""

        for item in response_json["content"]:
            if item["type"] == "text":
                if response_text != "":
                    response_text += "\n"
                response_text += item["text"]

        return response_text


    def get_response_from_image(self, text: str, image: Image.Image) -> str:

        buffered = BytesIO()

        rgb_image = image.convert('RGB')
        rgb_image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json',
        }

        data = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": img_base64,
                            }
                        },
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ]
        }

        response = requests.post(self.api_endpoint, headers=headers, data=json.dumps(data))
        response_json = response.json()

        response_text = ""

        for item in response_json["content"]:
            if item["type"] == "text":
                if response_text != "":
                    response_text += "\n"
                response_text += item["text"]

        return response_text
