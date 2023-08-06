from .abc import Snowflake
from .user import User
from .guild import Guild

from attrs import define, field
from datetime import datetime

__all__ = ("GuildTemplate",)


@define()
class GuildTemplate:
    """
    Represents the template of a guild from Discord.

    Attributes
    ----------
    code : `str`
        The template code as unique ID.
    name : `str`
        The name of the template.
    description : `str`, optional
        The description of the template, if any.
    usage_count : `int`
        The amount of times this template has been used.
    creator_id : `Snowflake`
        The ID of the user who created the template.
    creator : `User`
        The user who created the template.
    created_at : `datetime`
        When this template was created.
    updated_at : `datetime`
        When this template was last synced to the source guild.
    source_guild_id : `Snowflake`
        The ID of the guild this template is based on.
    serialized_source_guild : `Guild`
        The guild snapshot this template contains.
    is_dirty : `bool`
        Whether the template has unsynced changes or not.
    """

    code: str = field()
    """The template code as unique ID."""
    name: str = field()
    """The name of the template."""
    description: str | None = field(default=None)
    """The description of the template, if any."""
    usage_count: int = field()
    """The amount of times this template has been used."""
    creator_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the user who created the template."""
    creator: dict | User = field(converter=User)
    """The user who created the template."""
    created_at: str | datetime = field(converter=datetime.fromisoformat)
    """When this template was created."""
    updated_at: str | datetime = field(converter=datetime.fromisoformat)
    """When this template was last synced to the source guild."""
    source_guild_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the guild this template is based on."""
    serialized_source_guild: dict | Guild = field(converter=Guild)
    """The guild snapshot this template contains."""
    is_dirty: bool = field(default=False)
    """Whether the template has unsynced changes or not."""
