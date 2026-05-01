class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class AuthorizationError(DomainError):
    pass
