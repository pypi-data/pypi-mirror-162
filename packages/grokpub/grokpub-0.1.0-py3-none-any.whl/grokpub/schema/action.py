from uuid import UUID

from . import BaseModelSchema


class ActionSchema(BaseModelSchema):
    id: UUID
    name: str
    icon: str
    api: str
    num: int
    method: str
