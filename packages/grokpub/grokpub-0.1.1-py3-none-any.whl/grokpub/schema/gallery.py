from typing import List

from ..field import (
    CoverField,
    DescriptionField,
    Field,
    LinkField,
    TimestampField,
    TitleField,
)
from ..utils import unique
from . import BaseModelSchema
from .user import Author


class GalleryObject(BaseModelSchema):
    id: str = Field(default=unique.ulid("Gallery"))
    type: str = "gallery"
    title: str = TitleField()
    cover: str = CoverField()
    description: str = DescriptionField()
    images: List[str] = Field(default_factory=list)
    author: Author = Field(default_factory=Author)
    publishedAt: int = TimestampField()
    link: str = LinkField()
