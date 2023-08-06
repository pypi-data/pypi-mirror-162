from uuid import UUID

class Msp360Exception(Exception):
    pass


class ClientError(Msp360Exception):
    pass


class ResourceNotFound(ClientError):
    pass


# TODO: leverage messages in responses
def check_uuid(value: str, not_found=True, msg=None):
    '''Checks the value is a valid UUID if a resource was not found.
    '''
    try:
        UUID(value)
    except ValueError:
        raise ValueError(value) from None
    if not_found:
        raise ResourceNotFound(msg or value) from None
    else:
        raise ClientError(msg or value) from None
