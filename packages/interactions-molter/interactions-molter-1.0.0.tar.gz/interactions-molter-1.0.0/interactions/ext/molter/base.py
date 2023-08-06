import typing

import interactions
from .context import MolterContext
from .manager import MolterManager
from interactions import ext

__all__ = (
    "__version__",
    "version",
    "base",
    "setup",
)

__version__ = "1.0.0"


version = ext.Version(
    version=__version__,
    authors=[ext.VersionAuthor("Astrea49")],
)

base = ext.Base(
    name="interactions-molter",
    version=version,
    link="https://github.com/interactions-py/molter/",
    description=(
        "An extension library for interactions.py to add prefixed commands. A"
        " demonstration of molter-core."
    ),
    packages=["interactions.ext.molter"],
    requirements=["discord-py-interactions>=4.3.0"],
)


def setup(
    client: interactions.Client,
    *,
    default_prefix: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    generate_prefixes: typing.Optional[
        typing.Callable[
            [interactions.Client, interactions.Message],
            typing.Coroutine[
                typing.Any, typing.Any, typing.Union[str, typing.Iterable[str]]
            ],
        ]
    ] = None,
    on_molter_command_error: typing.Optional[
        typing.Callable[[MolterContext, Exception], typing.Coroutine]
    ] = None,
    **kwargs,
) -> MolterManager:
    """
    Allows setup of Molter through normal extension loading.
    It is recommended to use this function directly, though.

    Parameters:
        client: The client instance.
        default_prefix: \
            The default prefix to use. Defaults to ``None``.
        generate_prefixes (typing.Optional[typing.Callable]): An asynchronous function \
            that takes in a :class:`~interactions.client.bot.Client` and \
            :class:`~interactions.api.models.message.Message` object and returns either a \
            string or an iterable of strings. Defaults to ``None``.
        on_molter_command_error (typing.Optional[typing.Callable]): An asynchronous function \
            that takes in a :class:`.MolterContext` and :class:`Exception` to handle errors that occur \
            when running Molter commands. By default, Molter will output the error to \
            the default logging place and ignore it. The error event can also be listened \
            to by listening to the "on_molter_command_error" event.

            If neither ``default_prefix`` or ``generate_prefixes`` are provided, the bot
            defaults to using it being mentioned as its prefix.

    Returns:
        MolterManager: The class that deals with all things Molter.
    """
    return MolterManager(
        client=client,
        default_prefix=default_prefix,
        generate_prefixes=generate_prefixes,
        on_molter_command_error=on_molter_command_error,
        **kwargs,
    )
