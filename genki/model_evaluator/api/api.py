
from abc import ABC, abstractmethod
from PIL import Image

class GPTAPI(ABC):

    @abstractmethod
    def get_response_from_text(self, text: str) -> str:
        pass

    @abstractmethod
    def get_response_from_image(self, text: str, image: Image.Image) -> str:
        pass
