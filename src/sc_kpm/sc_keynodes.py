"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

from logging import Logger, getLogger
from typing import Dict, Optional

from sc_client import client
from sc_client.constants.exceptions import InvalidValueError
from sc_client.constants.sc_types import ScType
from sc_client.models import ScAddr, ScIdtfResolveParams

Idtf = str


class ScKeynodesMeta(type):
    """Metaclass to use ScKeynodes without creating an instance of a class"""

    def __init__(cls, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        cls._dict: Dict[Idtf, ScAddr] = {}
        cls._logger: Logger = getLogger(f"{__name__}.{cls.__name__}")

    def __call__(cls, *args, **kwargs):
        raise TypeError(f"Use {cls.__name__} without initialization")

    def __getitem__(cls, identifier: Idtf) -> ScAddr:
        """Get keynode, cannot be invalid ScAddr(0)"""
        addr = cls.get(identifier)  # pylint: disable=no-value-for-parameter
        if not addr.is_valid():
            cls._logger.error("Failed to get ScAddr by %s keynode: ScAddr is invalid", identifier)
            raise InvalidValueError(f"ScAddr of {identifier} is invalid")
        return addr

    def get(cls, identifier: Idtf) -> ScAddr:
        """Get keynode, can be ScAddr(0)"""
        return cls.resolve(identifier, None)  # pylint: disable=no-value-for-parameter

    def resolve(cls, identifier: Idtf, sc_type: Optional[ScType]) -> ScAddr:
        """Get keynode. If sc_type is valid, an element will be created in the KB"""
        addr = cls._dict.get(identifier)
        if addr is None:
            params = ScIdtfResolveParams(idtf=identifier, type=sc_type)
            addr = client.resolve_keynodes(params)[0]
            if addr.is_valid():
                cls._dict[identifier] = addr
            cls._logger.debug("Resolved %s identifier with type %s: %s", repr(identifier), repr(sc_type), repr(addr))
        return addr


class ScKeynodes(metaclass=ScKeynodesMeta):
    """Class which provides the ability to cache the identifier and ScAddr of keynodes stored in the KB."""
