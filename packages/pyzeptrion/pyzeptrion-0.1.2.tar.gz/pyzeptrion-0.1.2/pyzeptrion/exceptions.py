"""All exceptions for the Zeptrion Python bindings."""


class ZeptrionError(Exception):
    """General ZeptrionError exception occurred."""

    pass


class ZeptrionConnectionError(ZeptrionError):
    """When a connection error is encountered."""

    pass
