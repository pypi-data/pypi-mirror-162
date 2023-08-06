import uuid


def is_uuid(s: str) -> bool:
    try:
        uuid.UUID(str(s), version=4)
        return True
    except ValueError:
        return False
