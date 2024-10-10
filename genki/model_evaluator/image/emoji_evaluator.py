from genki.model_evaluator.api.api import GPTAPI
from genki.model_evaluator.api.claude_api import ClaudeAPI
from PIL import Image
import re

class EmojiEvaluator:
    def __init__(self, character_name: str, api: GPTAPI):
        self.api = api
        self.character_name = character_name

    def is_character_included(self, image: Image.Image) -> bool:
        prompt = f"Is the character ${self.character_name} included in the given image? Return YES or NO without anything else."
        resp = self.api.get_response_from_image(prompt, image)
        return re.search("yes", resp, re.IGNORECASE)


if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv()

    evaluator = EmojiEvaluator("Pepe", ClaudeAPI())
    img = Image.open("pepe.png")

    is_pepe = evaluator.is_character_included(img)

    if is_pepe:
        print("Using Pepe: Pepe included!")
    else:
        print("Using Pepe: Pepe not included!")

    cat = Image.open("cat.png")

    is_pepe = evaluator.is_character_included(cat)

    if is_pepe:
        print("Using cat: Pepe included!")
    else:
        print("Using cat: Pepe not included!")
