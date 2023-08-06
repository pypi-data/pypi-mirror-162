from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from tygle.base import RESTs


class Resource(BaseModel):
    __rests__: ClassVar["RESTs"]

    class Config:
        use_enum_values = True
