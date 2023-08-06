from typing import List

from ..field import (
    AvatarField,
    DescriptionField,
    Field,
    GenderField,
    IDField,
    NameField,
)
from ..utils import unique
from . import BaseModelSchema


class Author(BaseModelSchema):
    id: str = IDField(default=unique.ulid("Author"))
    name: str = NameField()
    gender: str = GenderField()
    description: str = DescriptionField()
    avatar: str = AvatarField()
    socials: List[str] = Field(default_factory=list)
