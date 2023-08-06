from enum import Enum

from ..field import (
    DescriptionField,
    DurationField,
    Field,
    LinkField,
    NameField,
    ResourceField,
    ThumbnailField,
    TimestampField,
)
from ..utils import unique
from . import BaseModelSchema
from .user import Author


class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class VideoSchema(BaseModelSchema):
    id: str = Field(default=unique.ulid("Video"))
    type: str = "video"
    orientation: Orientation = Field(default=Orientation.HORIZONTAL)
    thumbnail: str = ThumbnailField()
    name: str = NameField()
    description: str = DescriptionField()
    link: str = LinkField()
    duration: int = DurationField()
    resource: str = ResourceField()
    author: Author = Author()
    publishedAt: int = TimestampField()
