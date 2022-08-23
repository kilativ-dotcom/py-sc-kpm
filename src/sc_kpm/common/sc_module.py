"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at https://opensource.org/licenses/MIT)
"""

import logging
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List, Type, Union

from sc_client import client
from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr

from sc_kpm.common.sc_agent import ScAgentAbstract

logger = logging.getLogger(__name__)

RegisterParams = namedtuple("RegisterParams", "ScAgent element event_type")


class ScModuleAbstract(ABC):
    @abstractmethod
    def _register(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _unregister(self) -> None:
        raise NotImplementedError


class ScModule(ScModuleAbstract):
    _reg_params: List[RegisterParams] = []
    _agents: List[ScAgentAbstract] = []

    def register_agent(
        self, agent: Type[ScAgentAbstract], element: Union[str, ScAddr], event_type: ScEventType
    ) -> ScModuleAbstract:
        self._reg_params.append(RegisterParams(agent, element, event_type))
        return self

    def _register(self) -> None:
        if self._reg_params and not self._agents:
            if client.is_connected():
                for params in self._reg_params:
                    if not isinstance(params, RegisterParams):
                        raise TypeError("All elements of the module params list must be RegisterParams instance")
                    agent = params.ScAgent()
                    agent._register(params.element, params.event_type)  # pylint: disable=protected-access
                    self._agents.append(agent)
                logger.debug("%s is registered", self.__class__.__name__)
            else:
                raise RuntimeError("Cannot register agents: connection to the sc-server is not established")

    def _unregister(self) -> None:
        for agent in self._agents:
            agent._unregister()  # pylint: disable=protected-access
        self._agents.clear()
        logger.debug("%s is unregistered", self.__class__.__name__)
