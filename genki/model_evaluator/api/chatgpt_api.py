
from genki.model_evaluator.api.api import GPTAPI
from PIL import Image

class ChatGPTAPI(GPTAPI):

    def get_response_from_text(self, text: str) -> str:
        return ""

    def get_response_from_image(self, text: str, image: Image.Image) -> str:
        return ""
