from ..field import (
    CoverField,
    DescriptionField,
    Field,
    IconField,
    LinkField,
    NameField,
    TimestampField,
    URLField,
)
from ..utils import unique
from . import BaseModelSchema
from .user import Author


class ChannelSchema(BaseModelSchema):
    id: str = Field(default=unique.ulid("Gallery"))
    name: str = NameField()
    description: str = DescriptionField()
    maintainer: Author = Field(default_factory=Author)
    author: Author = Field(default_factory=Author)
    createdAt: int = TimestampField()
    latestPublishedAt: int = TimestampField()
    url: str = LinkField()
    feed_url: str = URLField()
    queryString: str = Field(default_factory=str)
    cover: str = CoverField()
    icon: str = IconField()
