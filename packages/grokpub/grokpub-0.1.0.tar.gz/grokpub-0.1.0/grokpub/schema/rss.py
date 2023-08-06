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


class RssObject(BaseModelSchema):
    id: str = Field(default=unique.ulid("Rss"))
    title: str = TitleField()
    content: str = ContentField()
    summary: str = SummaryField()
    cover: str = CoverField()
    link: str = LinkField()
    author: str = "Demo"
    publishedAt: int = TimestampField()
