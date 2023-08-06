from ..field import (
    CoverField,
    DescriptionField,
    DurationField,
    Field,
    LinkField,
    ResourceField,
    TimestampField,
    TitleField,
)
from ..utils import unique
from . import BaseModelSchema
from .user import Author


class Audio(BaseModelSchema):
    id: str = Field(default=unique.ulid("Audio"))
    type: str = "podcast"
    cover: str = CoverField()
    title: str = TitleField()
    description: str = DescriptionField()
    link: str = LinkField()
    duration: int = DurationField()
    resource: str = ResourceField()
    author: Author = Field(default_factory=Author)
    publishedAt: int = TimestampField()
