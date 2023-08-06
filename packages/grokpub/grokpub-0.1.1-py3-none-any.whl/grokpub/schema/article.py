from enum import Enum
from typing import List

from ..field import (
    ContentField,
    CoverField,
    Field,
    LinkField,
    SummaryField,
    TimestampField,
    TitleField,
)
from ..utils import unique
from . import BaseModelSchema
from .user import Author


class RenderType(str, Enum):
    STRING = "string"
    HTML = "html"
    MARKDOWN = "markdown"


class Content(BaseModelSchema):
    render: RenderType = Field(default=RenderType.STRING)
    conetnt: str = ContentField()


class ArticleSummary(BaseModelSchema):
    id: str = Field(default=unique.uuid("ArticleSummary"))
    title: str = TitleField()
    summary: str = SummaryField()
    cover: str = CoverField()
    author: Author = Field(default_factory=Author)
    publishedAt: int = TimestampField()
    link: str = LinkField()


class Article(BaseModelSchema):
    id: str = Field(default=unique.uuid("Article"))
    title: str = TitleField()
    cover: str = CoverField()
    author: Author = Field(default_factory=Author)
    summary: str = SummaryField()
    content: Content = Field(default_factory=Content)
    tags: List[str] = Field(default_factory=list)
    publishedAt: int = TimestampField()
    link: str = LinkField()
