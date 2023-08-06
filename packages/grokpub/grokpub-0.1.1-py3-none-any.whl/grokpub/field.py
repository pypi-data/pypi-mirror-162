from pydantic import Field

from . import utils


def VersionField(**kwargs) -> Field:
    default = {
        "default": "https://grok.pub/version/1.0",
        "description": "version",
    }
    default.update(kwargs)
    return Field(**default)


def DurationField(**kwargs) -> Field:
    default = {
        "default": 0,
        "example": 918,
    }
    default.update(kwargs)
    return Field(**default)


def TimestampField(**kwargs) -> Field:
    default = {
        "default": utils.now_timestamps(),
        "example": 1659877524,
    }
    default.update(kwargs)
    return Field(**default)


def IDField(**kwargs) -> Field:
    default = {
        "default": "6YWZ5XGKKC904TKMFZZ9D7SHXR",
        "example": "6YWZ5XGKKC904TKMFZZ9D7SHXR",
    }
    default.update(kwargs)
    return Field(**default)


def ULIDField(**kwargs) -> Field:
    default = {
        "min_length": 26,
        "max_length": 26,
        "example": "6YWZ5XGKKC904TKMFZZ9D7SHXR",
        "description": "ulid string",
    }
    default.update(kwargs)
    return Field(**default)


def ThumbnailField(**kwargs) -> Field:
    default = {
        "default": "https://lumiere-a.akamaihd.net/v1/images/apple-icon-180x180_25e12c79.png",
    }
    default.update(kwargs)
    return Field(**default)

def ImageField(**kwargs) -> Field:
    default = {
        "default": "https://lumiere-a.akamaihd.net/v1/images/apple-icon-180x180_25e12c79.png",
    }
    default.update(kwargs)
    return Field(**default)


def IconField(**kwargs) -> Field:
    default = {
        "default": "https://lumiere-a.akamaihd.net/v1/images/apple-icon-180x180_25e12c79.png",
        "description": "avatar url string",
    }
    default.update(kwargs)
    return Field(**default)

def CoverField(**kwargs) -> Field:
    default = {
        "default": "https://lumiere-a.akamaihd.net/v1/images/apple-icon-180x180_25e12c79.png",
        "description": "avatar url string",
    }
    default.update(kwargs)
    return Field(**default)


def AvatarField(**kwargs) -> Field:
    default = {
        "default": "https://lumiere-a.akamaihd.net/v1/images/apple-icon-180x180_25e12c79.png",
    }
    default.update(kwargs)
    return Field(**default)


def LinkField(**kwargs) -> Field:
    default = {
        "default": "https://grok.pub",
        "example": "https://grok.pub",
    }
    default.update(kwargs)
    return Field(**default)


def ResourceField(**kwargs) -> Field:
    default = {
        "default": "https://example.grok.pub/resouce.mp4",
        "example": "https://example.grok.pub/resouce.mp4",
    }
    default.update(kwargs)
    return Field(**default)


def URLField(**kwargs) -> Field:
    default = {
        "default": "https://grok.pub",
        "example": "https://grok.pub",
        "description": "url string",
    }
    default.update(kwargs)
    return Field(**default)


def SummaryField(**kwargs) -> Field:
    default = {
        "default": "历史不会重演，但它总会有惊人的相似。history doesn't repeat itself but it often rhymes.",
        "description": "content",
    }
    default.update(kwargs)
    return Field(**default)


def ContentField(**kwargs) -> Field:
    default = {
        "default": "历史不会重演，但它总会有惊人的相似。history doesn't repeat itself but it often rhymes.",
        "description": "content",
    }
    default.update(kwargs)
    return Field(**default)


def TitleField(**kwargs) -> Field:
    default = {
        "default": "history doesn't repeat itself but it often rhymes.",
        "description": "description",
    }
    default.update(kwargs)
    return Field(**default)


def DescriptionField(**kwargs) -> Field:
    default = {
        "default": "历史不会重演，但它总会有惊人的相似。history doesn't repeat itself but it often rhymes.",
        "description": "description",
    }
    default.update(kwargs)
    return Field(**default)


def GenderField(**kwargs) -> Field:
    default = {
        "default": "none",
        "example": "none or f or m",
        "description": "gender",
    }
    default.update(kwargs)
    return Field(**default)


def NameField(**kwargs) -> Field:
    default = {
        "default": "Yang",
        "example": "Grok.Pub",
        "description": "name string",
    }
    default.update(kwargs)
    return Field(**default)


def EmailField(**kwargs) -> Field:
    default = {
        "example": "name@coord.space",
        "description": "email string",
    }
    default.update(kwargs)
    return Field(**default)
