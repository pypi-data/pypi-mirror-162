import uuid


def object_uuid(name):
    return uuid.uuid3(uuid.NAMESPACE_OID, name)
