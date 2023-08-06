from typing import Any, List

from ..field import Field, LinkField, TimestampField
from ..utils import unique
from . import BaseModelSchema
from .action import ActionSchema


class MessageSchema(BaseModelSchema):
    id: str = Field(default=unique.ulid("Message"))
    type: str = Field(default="channel")
    publishedAt: int = TimestampField()
    body: Any = Field(default_factory=dict)
    actions: List[ActionSchema] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    link: str = LinkField()
