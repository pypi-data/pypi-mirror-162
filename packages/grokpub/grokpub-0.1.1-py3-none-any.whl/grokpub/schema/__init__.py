from typing import Any, Dict

from orjson import dumps, loads
from pydantic import BaseModel


class BaseModelSchema(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        require_by_default = False
        json_loads = loads
        json_dumps = dumps

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        if "exclude_none" in kwargs:
            _ignored = kwargs.pop("exclude_none")
        return super().dict(*args, exclude_none=True, **kwargs)


from .article import Article, ArticleSummary
from .audio import Audio
from .message import MessageSchema
from .video import VideoSchema

__all__ = [
    "Article",
    "VideoSchema",
    "ArticleSummary",
    "Audio",
    "MessageSchema",
]
