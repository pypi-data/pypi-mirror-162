from .user import User
from .guild import Guild, Member
from .channel import Channel
from ...utils.converters import optional_c, list_c
from .application import Application
from datetime import datetime

from attrs import define, field
from enum import IntEnum


class InviteTargetType(IntEnum):
    """
    Represents the targeted types of invites from Discord.

    Constants
    ---------
    STREAM
        The invite targets a stream.
    EMBEDDED_APPLICATION
        The invite targets an embedded application.
    """

    STREAM = 1
    """The invite targets a stream."""
    EMBEDDED_APPLICATION = 2
    """The invite targets an embedded application."""


@define()
class InviteStageInstance:
    """
    Represents an invite to a stage instance from Discord. This is deprecated.

    Attributes
    ----------
    members : `list[retux.Member]`
        The members speaking in the stage.
    participant_count : `int`
        The number of users in the stage.
    speaker_count : `int`
        The number of users speaking in the stage.
    topic : `str`
        The topic of the stage instance in-between 1-120 characters.
    """

    members: list[Member] = field(converter=list_c(Member))
    """The members speaking in the stage."""
    participant_count: int = field()
    """The number of users in the stage."""
    speaker_count: int = field()
    "The number of users speaking in the stage."
    topic: str = field()
    "The topic of the stage instance in-between 1-120 characters."


@define()
class Invite:
    """
    Represents an invite from Discord.

    Attributes
    ----------
    code : `str`
        The invite code.
    guild : `retux.Guild`, optional
        The guild this invite is for, if any.
    channel : `retux.Channel`, optional
        The channel this invite is for, if any.
    inviter : `retux.User`, optional
        The user who created the invite, if any.
    target_type : `InviteTargetType`, optional
        The type of target for a voice channel invite, if any.
    target_user : `retux.User`, optional
        The user whose stream to display for this voice channel stream invite, if any.
    target_application : `retux.Application`, optional
        The embedded application to open for this voice channel embedded application invite, if any.
    approximate_presence_count : `int`, optional
        Approximate count of online members, returned from the `Get Invites` endpoint
        when `with_counts=True`.
    approximate_member_count : `int`, optional
        Approximate count of total members, returned from the `Get Invites` endpoint
        when `with_counts=True`.
    expires_at : `datetime.datetime`, optional
        The expiration date of this invite, returned from the `Get Invites` endpoint
        when `with_expiration=True`.
    stage_instance : `InviteStageInstance`, optional
        Data of the instance if there is a public stage in the channel this invite is for. (deprecated)
    """

    code: str = field()
    """The invite code."""
    guild: dict | Guild | None = field(converter=optional_c(Guild), default=None)
    """The guild this invite is for, if any."""
    channel: dict | Channel | None = field(converter=optional_c(Channel), default=None)
    """The channel this invite is for, if any."""
    inviter: dict | User | None = field(converter=optional_c(User), default=None)
    """The user who created the invite, if any."""
    target_type: int | InviteTargetType | None = field(
        converter=optional_c(InviteTargetType), default=None
    )
    """The type of target for this voice channel invite, if any."""
    target_user: dict | User | None = field(converter=optional_c(User), default=None)
    """The user whose stream to display for this voice channel stream invite, if any."""
    target_application: dict | Application | None = field(
        converter=optional_c(Application), default=None
    )
    """The embedded application to open for this voice channel embedded application invite, if any"""
    approximate_presence_count: int | None = field(default=None)
    """Approximate count of online members, returned from the `Get Invites` endpoint when `with_counts=True`."""
    approximate_member_count: int | None = field(default=None)
    """Approximate count of total members, returned from the `Get Invites` endpoint when `with_counts=True`."""
    expires_at: str | datetime | None = field(
        converter=optional_c(datetime.fromisoformat), default=None
    )
    """The expiration date of this invite, returned from the `Get Invites` endpoint when `with_expiration=True`."""
    stage_instance: int | InviteStageInstance | None = field(
        converter=optional_c(InviteStageInstance), default=None
    )
    """Data of the instance if there is a public stage in the channel this invite is for. (deprecated)"""
    # guild_scheduled_event
    # """guild scheduled event data, only included if guild_scheduled_event_id contains a valid guild scheduled event id"""
    # TODO: Implement Guild Scheduled Event object
