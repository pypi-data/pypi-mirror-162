from uuid import NAMESPACE_DNS, UUID, uuid5

from ulid import ULID


def ulid(id) -> str:
    return str(ULID.from_uuid(uuid5(NAMESPACE_DNS, str(id))))


def uuid(name) -> UUID:
    namespace = NAMESPACE_DNS
    return uuid5(namespace, str(name))
