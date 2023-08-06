from typing import List, Optional

from ..field import (
    ContentField,
    DescriptionField,
    Field,
    IDField,
    LinkField,
    TimestampField,
)
from ..utils import unique
from . import BaseModelSchema
from .user import Author


class RetweetedObject(BaseModelSchema):
    id: str = IDField(default=unique.ulid("Retweeted"))
    content: str = ContentField()
    user: Author = Field(default_factory=Author)
    pictures: List[str] = Field(default_factory=list)
    link: str = LinkField()
    createdAt: int = TimestampField()


class TweetObject(BaseModelSchema):
    id: str = IDField(default=unique.ulid("Tweet"))
    content: str = DescriptionField()
    user: Author = Field(default_factory=Author)
    retweeted: Optional[RetweetedObject]
    pictures: List[str] = Field(default_factory=list)
    link: str = LinkField()
    createdAt: int = TimestampField()
