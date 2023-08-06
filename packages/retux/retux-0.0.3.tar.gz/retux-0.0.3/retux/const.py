from typing import TypeVar, Union


__version__ = "0.0.3"
__api_version__ = "v10"
__api_url__ = f"https://discord.com/api/{__api_version__}"
__gateway_url__ = "wss://gateway.discord.gg/"
__repo_url__ = "https://github.com/i0bs/retux"


class MISSING:
    """
    A sentinel that represents an argument with a "missing" value.
    This is used deliberately to avoid `None` space confusion.
    """

    pass


_T = TypeVar("_T")
NotNeeded = Union[_T, MISSING]
"""
A type variable to work alongside `MISSING`. This should only
be used to help further indicate an optional argument where it
already points to said type.
"""
