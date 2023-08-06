from typing import Any, Dict, List, Optional

from pydantic import Field

from ..field import TimestampField, VersionField
from ..schema import BaseModelSchema
from ..schema.message import MessageSchema


class ChannelFeedResponse(BaseModelSchema):
    version: str = VersionField()
    messages: List[Any] = []
    latestPublishedAt: int = TimestampField()
    since_id: Optional[str] = Field()
    max_id: Optional[str] = Field()

    @staticmethod
    def init_from_message_schema(messages: List[MessageSchema]):
        response = None
        if len(messages) > 0:
            latestPublishedAt = max(item.publishedAt for item in messages)
            if len(messages) > 0:
                max_id = messages[0].id
                since_id = messages[len(messages) - 1].id
            response = ChannelFeedResponse(**{
                "messages": messages,
                "since_id": since_id,
                "max_id": max_id,
                "latestPublishedAt": latestPublishedAt,
            })
        else:
            response = ChannelFeedResponse()
        return response

    @staticmethod
    def init_from_list_dict(messages: List[Dict]):
        latestPublishedAt = 0
        if len(messages) > 0:
            latestPublishedAt = messages[0]["publishedAt"]
            response = ChannelFeedResponse(**{
                "messages": messages,
                "latestPublishedAt": latestPublishedAt,
            })
        else:
            response = ChannelFeedResponse()
        return response

    class Config:
        orm_mode = False
