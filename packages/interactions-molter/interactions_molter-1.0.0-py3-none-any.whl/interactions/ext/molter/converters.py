import re
import typing

import interactions
import interactions.api.error as inter_errors
from . import errors
from . import utils
from .context import MolterContext
from .utils import _wrap_lib_exception

__all__ = (
    "MolterConverter",
    "NoArgumentConverter",
    "IDConverter",
    "SnowflakeConverter",
    "MemberConverter",
    "UserConverter",
    "ChannelConverter",
    "RoleConverter",
    "GuildConverter",
    "MessageConverter",
    "AttachmentConverter",
    "Greedy",
    "INTER_OBJECT_TO_CONVERTER",
)


T = typing.TypeVar("T")
T_co = typing.TypeVar("T_co", covariant=True)


@typing.runtime_checkable
class MolterConverter(typing.Protocol[T_co]):
    """A protocol representing a class used to convert an argument in Molter."""

    async def convert(self, ctx: MolterContext, argument: str) -> T_co:
        """
        The function that converts an argument to the appropriate type.
        This should be overridden by subclasses for their conversion logic.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            typing.Any: The converted argument.
        """

        raise NotImplementedError("Derived classes need to implement this.")


class NoArgumentConverter(typing.Generic[T_co]):
    """
    An indicator class for special types of converters that only uses the context.
    Arguments will be "eaten up" by converters otherwise.
    """

    async def convert(self, ctx: MolterContext, argument: str) -> T_co:
        raise NotImplementedError("Derived classes need to implement this.")


class _LiteralConverter(MolterConverter):
    values: typing.Dict

    def __init__(self, args: typing.Any):
        self.values = {arg: type(arg) for arg in args}

    async def convert(self, ctx: MolterContext, argument: str):
        for arg, converter in self.values.items():
            try:
                if (converted := converter(argument)) == arg:
                    return converted
            except Exception:
                continue

        literals_list = [str(a) for a in self.values.keys()]
        literals_str = ", ".join(literals_list[:-1]) + f", or {literals_list[-1]}"
        raise errors.BadArgument(
            f'Could not convert "{argument}" into one of {literals_str}.'
        )


_ID_REGEX = re.compile(r"([0-9]{15,})$")


class IDConverter(MolterConverter[T_co]):
    """The base converter for objects that have snowflake IDs."""

    @staticmethod
    def _get_id_match(argument):
        return _ID_REGEX.match(argument)


class SnowflakeConverter(IDConverter[interactions.Snowflake]):
    """
    Converts a string argument to a
    :class:`~interactions.api.models.misc.Snowflake`.
    """

    async def convert(self, _: MolterContext, argument: str) -> interactions.Snowflake:
        """
        Converts a given string to a :class:`~interactions.api.models.misc.Snowflake`.

        The lookup strategy is as follows:

        1. By raw snowflake ID.
        2. By role or channel mention.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            The converted object.
        """

        match = self._get_id_match(argument) or re.match(
            r"<(?:@(?:!|&)?|#)([0-9]{15,})>$", argument
        )

        if match is None:
            raise errors.BadArgument(f'"{argument}" is not a valid snowflake.')

        return interactions.Snowflake(match.group(1))


class MemberConverter(IDConverter[interactions.Member]):
    """
    Converts a string argument to a
    :class:`~interactions.api.models.member.Member` object.
    """

    def _get_member_from_list(self, members_data: typing.List[dict], argument: str):
        # sourcery skip: assign-if-exp
        result = None
        if len(argument) > 5 and argument[-5] == "#":
            result = next(
                (
                    m
                    for m in members_data
                    if f"{m['user']['username']}#{m['user']['discriminator']}"
                    == argument
                ),
                None,
            )

        if not result:
            result = next(
                (
                    m
                    for m in members_data
                    if m.get("nick") == argument or m["user"]["username"] == argument
                ),
                None,
            )

        if result is not None:
            return interactions.Member(**result)
        return result

    async def convert(self, ctx: MolterContext, argument: str) -> interactions.Member:
        """
        Converts a given string to a :class:`~interactions.api.models.member.Member`
        object. This will only work in guilds.

        The lookup strategy is as follows:

        1. By raw snowflake ID.
        2. By mention.
        3. By username + tag (ex User#1234).
        4. By nickname or username.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            The converted object.
        """
        if not ctx.guild or not ctx.guild_id:
            raise errors.BadArgument("This command cannot be used in private messages.")

        match = self._get_id_match(argument) or re.match(
            r"<@!?([0-9]{15,})>$", argument
        )
        result = None

        if match:
            result = await _wrap_lib_exception(
                interactions.get(
                    ctx.client,
                    interactions.Member,
                    parent_id=int(ctx.guild_id),
                    object_id=int(match.group(1)),
                )
            )
        else:
            query = argument
            if len(argument) > 5 and argument[-5] == "#":
                query, _, _ = argument.rpartition("#")

            members_data = await _wrap_lib_exception(
                ctx._http.search_guild_members(int(ctx.guild_id), query, limit=5)
            )

            if not members_data:
                raise errors.BadArgument(f'Member "{argument}" not found.')

            result = self._get_member_from_list(members_data, argument)

        if not result:
            raise errors.BadArgument(f'Member "{argument}" not found.')

        result._client = ctx._http
        return result


class UserConverter(IDConverter[interactions.User]):
    """
    Converts a string argument to a
    :class:`~interactions.api.models.user.User` object.
    """

    async def convert(self, ctx: MolterContext, argument: str) -> interactions.User:
        """
        Converts a given string to a :class:`~interactions.api.models.user.User` object.

        The lookup strategy is as follows:

        1. By raw snowflake ID.
        2. By mention.
        3. By username + tag (ex User#1234).
        4. By username.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            The converted object.
        """
        # sourcery skip: remove-redundant-pass
        match = self._get_id_match(argument) or re.match(
            r"<@!?([0-9]{15,})>$", argument
        )
        result = None

        if match:
            result = await _wrap_lib_exception(
                interactions.get(
                    ctx.client, interactions.User, object_id=int(match.group(1))
                )
            )
        else:
            all_cached_users = ctx._http.cache[interactions.User].values.values()
            if len(argument) > 5 and argument[-5] == "#":
                result = next(
                    (
                        u
                        for u in all_cached_users
                        if f"{u.username}#{u.discriminator}" == argument
                    ),
                    None,
                )

            if not result:
                result = next(
                    (u for u in all_cached_users if u.username == argument), None
                )

        if not result:
            raise errors.BadArgument(f'User "{argument}" not found.')

        result._client = ctx._http
        return result


class ChannelConverter(IDConverter[interactions.Channel]):
    """
    Converts a string argument to a
    :class:`~interactions.api.models.channel.Channel` object.
    """

    async def convert(
        self,
        ctx: MolterContext,
        argument: str,
    ) -> interactions.Channel:
        """
        Converts a given string to a :class:`~interactions.api.models.channel.Channel` object.

        The lookup strategy is as follows:

        1. By raw snowflake ID.
        2. By channel mention.
        3. By name - the bot will search in a guild if the context has it, otherwise it will search globally.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            The converted object.
        """
        match = self._get_id_match(argument) or re.match(r"<#([0-9]{15,})>$", argument)
        result = None

        if match:
            result = await _wrap_lib_exception(
                interactions.get(
                    ctx.client, interactions.Channel, object_id=int(match.group(1))
                )
            )
        elif ctx.guild and ctx.guild.channels:
            result = next(
                (
                    c
                    for c in ctx.guild.channels
                    if c.name == utils.remove_prefix(argument, "#")
                ),
                None,
            )

        if not result:
            raise errors.BadArgument(f'Channel "{argument}" not found.')

        result._client = ctx._http
        return result


class RoleConverter(IDConverter[interactions.Role]):
    """
    Converts a string argument to a
    :class:`~interactions.api.models.role.Role` object.
    """

    async def convert(
        self,
        ctx: MolterContext,
        argument: str,
    ) -> interactions.Role:
        """
        Converts a given string to a :class:`~interactions.api.models.role.Role` object.

        The lookup strategy is as follows:

        1. By raw snowflake ID.
        2. By mention.
        3. By name.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            The converted object.
        """

        if not ctx.guild_id or not ctx.guild:
            raise errors.BadArgument("This command cannot be used in private messages.")

        # while i'd like to use the cache here, roles don't store info about which guild they come
        # from, and the guild doesn't update its role list
        match = self._get_id_match(argument) or re.match(r"<@&([0-9]{15,})>$", argument)
        result = None

        if match:
            result = await _wrap_lib_exception(
                interactions.get(
                    ctx.client,
                    interactions.Role,
                    parent_id=int(ctx.guild_id),
                    object_id=int(match.group(1)),
                )
            )
        else:
            result = next(
                (r for r in ctx.guild.roles if r.name == argument),
                None,
            )

        if not result:
            raise errors.BadArgument(f'Role "{argument}" not found.')

        return interactions.Role(**result, _client=ctx._http)  # type: ignore


class GuildConverter(IDConverter[interactions.Guild]):
    """
    Converts a string argument to a
    :class:`~interactions.api.models.guild.Guild` object.
    """

    async def convert(self, ctx: MolterContext, argument: str) -> interactions.Guild:
        """
        Converts a given string to a :class:`~interactions.api.models.guild.Guild` object.

        The lookup strategy is as follows:

        1. By raw snowflake ID.
        2. By name.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            The converted object.
        """
        if match := self._get_id_match(argument):
            result = await _wrap_lib_exception(
                interactions.get(
                    ctx.client, interactions.Guild, object_id=int(match.group(1))
                )
            )
        else:
            result = next((g for g in ctx.bot.guilds if g.name == argument), None)

        if not result:
            raise errors.BadArgument(f'Guild "{argument}" not found.')

        result._client = ctx._http
        return result


class MessageConverter(MolterConverter[interactions.Message]):
    """
    Converts a string argument to a
    :class:`~interactions.api.models.message.Message` object.
    """

    # either just the id or <chan_id>-<mes_id>, a format you can get by shift clicking "copy id"
    _ID_REGEX = re.compile(
        r"(?:(?P<channel_id>[0-9]{15,})-)?(?P<message_id>[0-9]{15,})"
    )
    # of course, having a way to get it from a link is nice
    _MESSAGE_LINK_REGEX = re.compile(
        r"https?://[\S]*?discord(?:app)?\.com/channels/(?P<guild_id>[0-9]{15,}|@me)/"
        r"(?P<channel_id>[0-9]{15,})/(?P<message_id>[0-9]{15,})\/?$"
    )

    async def convert(self, ctx: MolterContext, argument: str) -> interactions.Message:
        """
        Converts a given string to a :class:`~interactions.api.models.message.Message` object.

        The lookup strategy is as follows:

        1. By raw snowflake ID. The message must be in the same channel as the context.
        2. By message + channel ID in the format of ``{Channel ID}-{Message ID}``. \
            This can be obtained by shift clicking "Copy ID" when Developer Mode is enabled.
        3. By message link.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            The converted object.
        """
        match = self._ID_REGEX.match(argument) or self._MESSAGE_LINK_REGEX.match(
            argument
        )
        if not match:
            raise errors.BadArgument(f'Message "{argument}" not found.')

        data = match.groupdict()

        message_id = int(data["message_id"])
        channel_id = (
            int(data["channel_id"]) if data.get("channel_id") else int(ctx.channel_id)
        )

        # this guild checking is technically unnecessary, but we do it just in case
        # it means a user cant just provide an invalid guild id and still get a message
        guild_id = data["guild_id"] if data.get("guild_id") else ctx.guild_id
        guild_id = str(guild_id) if guild_id != "@me" else None

        if cached_message := ctx._http.cache[interactions.Message].get(
            interactions.Snowflake(message_id)
        ):
            if int(cached_message.channel_id) == channel_id and (
                cached_message.guild_id == guild_id
                or str(cached_message.guild_id == guild_id)
            ):
                return cached_message
            else:
                raise errors.BadArgument(f'Message "{argument}" not found.')

        try:
            message_data: dict = await ctx._http.get_message(channel_id, message_id)  # type: ignore

            msg_guild_id: typing.Optional[str] = message_data.get("guild_id")
            if not msg_guild_id:
                if channel := ctx._http.cache[interactions.Channel].get(
                    interactions.Snowflake(channel_id)
                ):
                    msg_guild_id = message_data["guild_id"] = (
                        str(channel.guild_id) if channel.guild_id else None
                    )
                else:
                    channel_data = await _wrap_lib_exception(
                        ctx._http.get_channel(channel_id)
                    )
                    if channel_data:
                        msg_guild_id = message_data["guild_id"] = channel_data.get(
                            "guild_id"
                        )
                    else:
                        raise errors.BadArgument(f'Message "{argument}" not found.')

            if msg_guild_id != guild_id:
                raise errors.BadArgument(f'Message "{argument}" not found.')

            return interactions.Message(**message_data, _client=ctx._http)  # type: ignore
        except inter_errors.LibraryException:
            raise errors.BadArgument(f'Message "{argument}" not found.')


class AttachmentConverter(NoArgumentConverter[interactions.Attachment]):
    """A converter for handling attachments in a message."""

    async def convert(self, ctx: MolterContext, _) -> interactions.Attachment:
        """
        Returns an :class:`~interactions.api.models.message.Attachment`
        based on the following logic:

        - If this is the first time this converter is being run for this \
            message/context, get the first attachment.
        - If this is the second time this converter is being run for this \
            message/content, get the second attachment.
        - Repeat.
        - If there are no attachments on the message, or there is no more of \
            them, raise :class:`.BadArgument`.

        Args:
            ctx: The context to use for the conversion.
            _: An unneeded variable. Feel free to fill it in with anything.

        Returns:
            An attachment.
        """
        # could be edited by a dev, but... why
        attachment_counter: int = ctx.extras.get("__molter_attachment_counter", 0)

        try:
            attach = ctx.message.attachments[attachment_counter]
            ctx.extras["__molter_attachment_counter"] = attachment_counter + 1
            return attach
        except IndexError:
            raise errors.BadArgument("There are no more attachments for this context.")


class Greedy(typing.List[T]):
    """
    A special marker class to mark an argument in a Molter command to repeatedly
    convert until it fails to convert an argument.
    """

    pass


INTER_OBJECT_TO_CONVERTER: typing.Dict[type, typing.Type[MolterConverter]] = {
    interactions.Snowflake: SnowflakeConverter,
    interactions.Member: MemberConverter,
    interactions.User: UserConverter,
    interactions.Channel: ChannelConverter,
    interactions.Role: RoleConverter,
    interactions.Guild: GuildConverter,
    interactions.Message: MessageConverter,
    interactions.Attachment: AttachmentConverter,  # type: ignore
}
"""
A dictionary mapping of Discord models from interactions.py to its respective :class:`MolterConverter`.

The mapping is represented by the table below.
For prefixed commands, the model, if used as a type hint for a parameter, will use the corresponding converter to process an argument.

+-------------------------------------------------------+------------------------------+
| Discord Model                                         | Converter                    |
+=======================================================+==============================+
| :class:`~interactions.api.models.misc.Snowflake`      | :class:`SnowflakeConverter`  |
+-------------------------------------------------------+------------------------------+
| :class:`~interactions.api.models.member.Member`       | :class:`MemberConverter`     |
+-------------------------------------------------------+------------------------------+
| :class:`~interactions.api.models.user.User`           | :class:`UserConverter`       |
+-------------------------------------------------------+------------------------------+
| :class:`~interactions.api.models.channel.Channel`     | :class:`ChannelConverter`    |
+-------------------------------------------------------+------------------------------+
| :class:`~interactions.api.models.role.Role`           | :class:`RoleConverter`       |
+-------------------------------------------------------+------------------------------+
| :class:`~interactions.api.models.guild.Guild`         | :class:`GuildConverter`      |
+-------------------------------------------------------+------------------------------+
| :class:`~interactions.api.models.message.Message`     | :class:`MessageConverter`    |
+-------------------------------------------------------+------------------------------+
| :class:`~interactions.api.models.message.Attachment`  | :class:`AttachmentConverter` |
+-------------------------------------------------------+------------------------------+


:meta hide-value:
"""
