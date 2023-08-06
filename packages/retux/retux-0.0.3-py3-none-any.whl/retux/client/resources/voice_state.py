from .abc import Snowflake
from ...utils.converters import optional_c
from .guild import Member

from attrs import define, field
from datetime import datetime

__all__ = ("Voice", "VoiceState")


@define()
class VoiceState:
    """
    Represents the state of a user's VOIP from Discord.

    Attributes
    ----------
    guild_id : `Snowflake`, optional
        The guild ID this voice state is for.
    channel_id : `Snowflake`, optional
        The channel ID this user is connected to.
    user_id : `Snowflake`
        The user ID this voice state is for.
    member : `Member`, optional
        The guild member this voice state is for.
    session_id : `str`
        The session ID for this voice state.
    deaf : `bool`
        Whether this user is deafened by the server or not.
    mute : `bool`
        Whether this user is muted by the server or not.
    self_deaf : `bool`
        Whether this user is locally deafened or not.
    self_mute : `bool`
        Whether this user is muted by the server or not.
    self_stream : `bool`
        Whether this user is streaming using 'Go Live' or not.
    self_video : `bool`
        Whether this user's camera is enabled or not.
    suppress : `bool`
        Whether this user is muted by the current user or not.
    request_to_speak_timestamp : `datetime`, optional
        The time at which the user requested to speak, if present.
    """

    guild_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The guild ID this voice state is for."""
    channel_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The channel ID this user is connected to."""
    user_id: str | Snowflake = field(converter=Snowflake)
    """The user ID this voice state is for."""
    member: dict | Member | None = field(converter=optional_c(Member), default=None)
    """The guild member this voice state is for."""
    session_id: str = field()
    """The session ID for this voice state."""
    deaf: bool = field()
    """Whether this user is deafened by the server."""
    mute: bool = field()
    """Whether this user is muted by the server."""
    self_deaf: bool = field()
    """Whether this user is locally deafened."""
    self_mute: bool = field()
    """Whether this user is locally muted."""
    self_stream: bool = field(default=False)
    """Whether this user is streaming using 'Go Live'."""
    self_video: bool = field()
    """Whether this user's camera is enabled."""
    suppress: bool = field()
    """Whether this user is muted by the current user."""
    request_to_speak_timestamp: datetime | str | None = field(
        converter=optional_c(datetime.fromisoformat), default=None
    )
    """The time at which the user requested to speak."""


Voice = VoiceState
