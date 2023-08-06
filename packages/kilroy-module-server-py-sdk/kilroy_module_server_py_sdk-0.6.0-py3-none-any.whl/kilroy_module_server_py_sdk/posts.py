from abc import ABC
from typing import Optional

from kilroy_ws_server_py_sdk import SerializableModel
from pydantic import root_validator


class TextData(SerializableModel):
    content: str


class ImageData(SerializableModel):
    raw: str
    filename: str


class BasePost(SerializableModel, ABC):
    pass


class TextOnlyPost(BasePost):
    text: TextData


class ImageOnlyPost(BasePost):
    image: ImageData


class TextAndImagePost(BasePost):
    text: TextData
    image: ImageData


class TextOrImagePost(BasePost):
    text: Optional[TextData] = None
    image: Optional[ImageData] = None

    @root_validator(pre=True)
    def check_if_at_least_one_present(cls, values):
        if "text" not in values and "image" not in values:
            raise ValueError("Any of text or image is required.")
        return values

    class Config:
        schema_extra = {
            "anyOf": [
                {"required": ["text"]},
                {"required": ["image"]},
            ]
        }


class TextWithOptionalImagePost(BasePost):
    text: TextData
    image: Optional[ImageData] = None


class ImageWithOptionalTextPost(BasePost):
    text: Optional[TextData] = None
    image: ImageData
