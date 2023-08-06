import inspect
import logging
import sys
import traceback
import typing

import interactions
from . import utils
from .command import MolterCommand
from .context import MolterContext

logger: logging.Logger = logging.getLogger("molter")

__all__ = ("MolterInjectedClient", "MolterManager")


class MolterInjectedClient(interactions.Client):
    """
    A semi-stub for :class:`Clients <interactions.client.bot.Client>`
    injected with Molter. This should only be used for type hinting.
    """

    molter: "MolterManager"
    "The Molter manager for this client."


class MolterManager:
    """
    The main part of the extension. Deals with injecting itself in the first place.

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
    """

    def __init__(
        self,
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
    ) -> None:
        # typehinting funkyness for better typehints
        client = typing.cast(MolterInjectedClient, client)

        self.client = client
        self.default_prefix = default_prefix
        self.prefixed_commands: typing.Dict[str, MolterCommand] = {}

        if default_prefix is None and generate_prefixes is None:
            # by default, use mentioning the bot as the prefix
            generate_prefixes = utils.when_mentioned

        self.generate_prefixes = (  # type: ignore
            generate_prefixes
            if generate_prefixes is not None
            else self.generate_prefixes
        )
        self.on_molter_command_error = (  # type: ignore
            on_molter_command_error
            if on_molter_command_error is not None
            else self.on_molter_command_error
        )

        # this allows us to use a (hopefully) non-conflicting namespace
        self.client.molter = self

        # i hope someone dies internally when looking at this /lhj
        # but the general idea is that we want to process commands
        # from the main file right before starting up, so that we have a full
        # list of commands (otherwise, we may only get a partial list)

        # since we can pretty much guarantee that the ready function will only be
        # ran at the end for a variety of reasons, we can hook onto this
        # rather easily without many problems... unless someone's adding commands
        # after the bot has started, to which they should be using add_prefixed_command
        # anyways.
        def cursed_override(old_ready):
            async def new_ready():
                for _, func in inspect.getmembers(
                    sys.modules["__main__"],
                    predicate=lambda x: isinstance(x, MolterCommand)
                    and not x.is_subcommand(),
                ):
                    self.add_prefixed_command(func)
                await old_ready()

            return new_ready

        self.client._ready = cursed_override(self.client._ready)

        self.client.event(self._handle_prefixed_commands, name="on_message_create")  # type: ignore
        self.client.event(self.on_molter_command_error, name="on_molter_command_error")  # type: ignore

    def add_prefixed_command(self, command: MolterCommand) -> None:
        """
        Add a prefixed command to the client.

        Args:
            command: The command to add.
        """
        if command.is_subcommand():
            raise ValueError(
                "You cannot add subcommands to the client - add the base command"
                " instead."
            )

        command._parse_parameters()

        if self.prefixed_commands.get(command.name):
            raise ValueError(
                "Duplicate command! Multiple commands share the name/alias:"
                f" {command.name}."
            )
        self.prefixed_commands[command.name] = command

        for alias in command.aliases:
            if self.prefixed_commands.get(alias):
                raise ValueError(
                    "Duplicate command! Multiple commands share the name/alias:"
                    f" {alias}."
                )
            self.prefixed_commands[alias] = command

    def get_prefixed_command(self, name: str) -> typing.Optional[MolterCommand]:
        """
        Gets a command by the name/alias specified.

        This function is able to resolve subcommands - fully qualified names can be used.
        For example, passing in ``foo bar`` would get the subcommand ``bar`` from the
        command ``foo``.

        Args:
            name: The name of the command to search for.

        Returns:
            The command object, if found.
        """
        if " " not in name:
            return self.prefixed_commands.get(name)

        names = name.split()
        if not names:
            return None

        cmd = self.prefixed_commands.get(names[0])
        if not cmd:
            return cmd

        for name in names[1:]:
            try:
                cmd = cmd.subcommands[name]
            except (AttributeError, KeyError):
                return None

        return cmd

    def _remove_cmd_and_aliases(self, name: str):
        if cmd := self.prefixed_commands.pop(name, None):
            for alias in cmd.aliases:
                self.prefixed_commands.pop(alias, None)

    def remove_prefixed_command(
        self, name: str, delete_parent_if_empty: bool = False
    ) -> typing.Optional[MolterCommand]:
        """
        Removes a command if it exists.
        If an alias is specified, only the alias will be removed.

        This function is able to resolve subcommands - fully qualified names can be used.
        For example, passing in ``foo bar`` would delete the subcommand ``bar``
        from the command ``foo``.

        Args:
            name: The command to remove.
            delete_parent_if_empty: Should the parent command be deleted if it \
                ends up having no subcommands after deleting the command specified? \
                Defaults to ``False``.

        Returns:
            The command that was removed, if one was. If the command was not found,
            this function returns ``None``.
        """
        command = self.get_prefixed_command(name)

        if command is None:
            return None

        if name in command.aliases:
            command.aliases.remove(name)
            return command

        if command.parent:
            command.parent.remove_command(command.name)
        else:
            self._remove_cmd_and_aliases(command.name)

        if delete_parent_if_empty:
            while command.parent is not None and not command.parent.subcommands:
                if command.parent.parent:
                    _new_cmd = command.parent
                    command.parent.parent.remove_command(command.parent.name)
                    command = _new_cmd
                else:
                    self._remove_cmd_and_aliases(command.parent.name)
                    break

        return command

    async def generate_prefixes(
        self, client: interactions.Client, msg: interactions.Message
    ) -> typing.Union[str, typing.Iterable[str]]:
        """
        Generates a list of prefixes a prefixed command can have based on the client and message.
        This can be overwritten by passing a function to generate_prefixes on initialization.

        Args:
            client: The client instance.
            msg: The message sent.

        Returns:
            The prefix(es) to check for.
        """
        return self.default_prefix  # type: ignore

    async def on_molter_command_error(
        self, context: MolterContext, error: Exception
    ) -> None:
        """
        A function that is called when a Molter command errors out.
        By default, this function outputs to the default logging place.

        Args:
            context: The context in which the error occurred.
            error: The exception raised by the Molter command.
        """

        out = traceback.format_exception(type(error), error, error.__traceback__)
        logger.error(
            "Ignoring exception in {}:{}{}".format(
                f"Molter cmd / {context.invoked_name}",
                "\n" if len(out) > 1 else " ",
                "".join(out),
            ),
        )

    async def _create_context(self, msg: interactions.Message) -> MolterContext:
        """
        Creates a `MolterContext` object from the given message.

        Args:
            msg (`interactions.Message`): The message to create a context from.

        Returns:
            `MolterContext`: The context generated.
        """
        # weirdly enough, sometimes this isn't set right
        msg._client = self.client._http

        channel = await interactions.get(
            self.client, interactions.Channel, object_id=int(msg.channel_id)
        )

        if (guild_id := msg.guild_id) or (guild_id := channel.guild_id):
            guild = await utils._wrap_lib_exception(
                interactions.get(
                    self.client, interactions.Guild, object_id=int(guild_id)
                )
            )
        else:
            guild = None

        return MolterContext(  # type: ignore
            client=self.client,
            message=msg,
            user=msg.author,  # type: ignore
            member=msg.member,
            channel=channel,
            guild=guild,
        )

    async def _handle_prefixed_commands(self, msg: interactions.Message):
        """
        Determines if a command is being triggered and dispatch it.

        Args:
            msg (`interactions.Message`): The message created.
        """

        if not msg.content or msg.author.bot:
            return

        prefixes = await self.generate_prefixes(self.client, msg)

        if isinstance(prefixes, str):
            # its easier to treat everything as if it may be an iterable
            # rather than building a special case for this
            prefixes = (prefixes,)

        if prefix_used := next(
            (prefix for prefix in prefixes if msg.content.startswith(prefix)), None
        ):
            context = await self._create_context(msg)
            context.prefix = prefix_used
            context.content_parameters = utils.remove_prefix(msg.content, prefix_used)
            command = self.client.molter

            while True:
                first_word: str = utils.get_first_word(context.content_parameters)  # type: ignore
                if isinstance(command, MolterCommand):
                    new_command = command.subcommands.get(first_word)
                else:
                    new_command = command.prefixed_commands.get(first_word)
                if not new_command or not new_command.enabled:
                    break

                command = new_command
                context.content_parameters = utils.remove_prefix(
                    context.content_parameters, first_word
                ).strip()

                if command.subcommands and command.hierarchical_checking:
                    try:
                        await command._run_checks(context)
                    except Exception as e:
                        if command.error_callback:
                            await command.error_callback(context, e)  # type: ignore
                        elif command.extension and command.extension._error_callback:
                            await command.extension._error_callback(context, e)
                        else:
                            self.client._websocket._dispatch.dispatch(
                                "on_molter_command_error", context, e
                            )
                        return

            if isinstance(command, MolterManager):
                command = None

            if command and command.enabled:
                # this looks ugly, ik
                context.invoked_name = utils.remove_suffix(
                    utils.remove_prefix(msg.content, prefix_used),
                    context.content_parameters,
                ).strip()
                context.args = utils.get_args_from_str(context.content_parameters)
                context.command = command

                try:
                    self.client._websocket._dispatch.dispatch(
                        "on_molter_command", context
                    )
                    await command(context)
                except Exception as e:
                    if command.error_callback:
                        await command.error_callback(context, e)  # type: ignore
                    elif command.extension and command.extension._error_callback:
                        await command.extension._error_callback(context, e)
                    else:
                        self.client._websocket._dispatch.dispatch(
                            "on_molter_command_error", context, e
                        )
                finally:
                    self.client._websocket._dispatch.dispatch(
                        "on_molter_command_complete", context
                    )
