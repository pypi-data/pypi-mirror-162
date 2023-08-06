import inspect
import typing

import interactions
from . import utils
from .command import MolterCommand
from .context import MolterContext

if typing.TYPE_CHECKING:
    from .manager import MolterInjectedClient

__all__ = ("MolterExtensionMixin", "MolterExtension")


class MolterExtensionMixin:
    """
    A mixin that can be used to add Molter functionality into any subclass of
    interactions.py's extensions. Simply use it like so: ::

        class MyExt(MolterExtensionMixin, ActualExtension):
            ...
    """

    _error_callback: typing.Optional[
        typing.Callable[[MolterContext, Exception], typing.Coroutine]
    ] = None
    _molter_prefixed_commands: typing.List[MolterCommand]

    def __new__(cls, client: interactions.Client, *args, **kwargs):
        self = super().__new__(cls, client, *args, **kwargs)  # type: ignore
        self._molter_prefixed_commands = []
        error_handler_count = 0

        self.client = typing.cast("MolterInjectedClient", self.client)

        for _, func in inspect.getmembers(
            self,
            predicate=lambda x: isinstance(x, MolterCommand)
            or hasattr(x, "__ext_molter_error__"),
        ):
            if isinstance(func, MolterCommand):
                cmd: MolterCommand = func

                if not cmd.is_subcommand():  # we don't want to add subcommands
                    cmd = utils._wrap_recursive(cmd, self)
                    self._molter_prefixed_commands.append(cmd)
                    self.client.molter.add_prefixed_command(cmd)
            elif hasattr(func, "__ext_molter_error__"):
                if error_handler_count >= 1:
                    raise ValueError(
                        "A Molter extension cannot have more than one Molter command"
                        " error handler."
                    )

                self._error_callback = func
                error_handler_count += 1

        return self

    async def teardown(self, *args, **kwargs) -> None:
        self.client = typing.cast("MolterInjectedClient", self.client)

        for cmd in self._molter_prefixed_commands:
            names_to_remove = cmd.aliases.copy()
            names_to_remove.append(cmd.name)

            for name in names_to_remove:
                self.client.molter.prefixed_commands.pop(name, None)

        return await super().teardown(*args, **kwargs)  # type: ignore


class MolterExtension(MolterExtensionMixin, interactions.Extension):
    """
    An extension that allows you to use Molter commands in them.
    You should use this if you only intend on using Molter in an extension,
    and not any other feature from any other extension.
    """

    pass
