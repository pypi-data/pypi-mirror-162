import dataclasses
import typing

try:
    # Only available in 3.9+
    from typing import Annotated
except ImportError:  # pragma: no cover
    from typing_extensions import Annotated  # pragma: no cover

T = typing.TypeVar("T")


class MissingSentinel(typing.Generic[T]):
    """
    Class to detect when a field is not initialized
    """

    ...


@dataclasses.dataclass
class Fixed(typing.Generic[T]):
    """
    Represents an Avro Fixed type

    size (int): Specifying the number of bytes per value
    """

    size: int
    default: typing.Any = dataclasses.field(default=MissingSentinel)
    namespace: typing.Optional[str] = None
    aliases: typing.Optional[typing.List] = None
    _dataclasses_custom_type: str = "Fixed"

    def __repr__(self) -> str:
        return f"{self.size}"


@dataclasses.dataclass
class Decimal(typing.Generic[T]):
    """
    Represents an Avro Decimal type
    precision (int): Specifying the number precision
    scale(int): Specifying the number scale. Default 0
    """

    precision: int
    scale: int = 0
    default: typing.Any = dataclasses.field(default=MissingSentinel)
    _dataclasses_custom_type: str = "Decimal"

    # Decimal serializes to bytes, which doesn't support namespace
    aliases: typing.Optional[typing.List] = None

    def __repr__(self) -> str:
        return f"Decimal precision: {self.precision} scale:{self.scale}"


Int32 = Annotated[int, "Int32"]
Float32 = Annotated[float, "Float32"]


CUSTOM_TYPES = ("Fixed", "Decimal", "Int32", "Float32")
