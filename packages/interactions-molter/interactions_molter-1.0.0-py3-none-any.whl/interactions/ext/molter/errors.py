import typing

from .utils import escape_mentions

if typing.TYPE_CHECKING:
    from .context import MolterContext


__all__ = ("MolterException", "BadArgument", "CheckFailure")


class MolterException(Exception):
    """The base exception for Molter exceptions."""

    pass


class BadArgument(MolterException):
    """
    A special exception for invalid arguments when using Molter commands.

    Parameters:
        message: The message to use for the exception.
        args: Various arguments to use for the exception.
    """

    def __init__(self, message: typing.Optional[str] = None, *args: typing.Any) -> None:
        if message is not None:
            message = escape_mentions(message)
            super().__init__(message, *args)
        else:
            super().__init__(*args)


class CheckFailure(MolterException):
    """
    An exception when a check fails.

    Arguments:
        context: The context for this check.
        message: The error message.
        check (typing.Callable): The check that failed. This is \
            automatically passed in if the check fails - there is \
            no need to do it yourself.
    """

    def __init__(
        self,
        context: "MolterContext",
        message: typing.Optional[str] = "A check has failed.",
        *,
        check: typing.Callable[
            ["MolterContext"], typing.Coroutine[typing.Any, typing.Any, bool]
        ] = None,
    ):
        self.context = context
        self.check = check
        self.message = message

        super().__init__(message)
