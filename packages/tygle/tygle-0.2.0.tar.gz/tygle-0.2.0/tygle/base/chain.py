from pydantic import BaseModel, PrivateAttr

from .rest import REST


class Chain(BaseModel):
    _rest: REST = PrivateAttr()
