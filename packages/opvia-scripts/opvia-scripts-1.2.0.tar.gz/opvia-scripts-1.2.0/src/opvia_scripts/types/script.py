import logging
from abc import ABC, abstractmethod
from typing import Dict, List
from uuid import uuid4

from fastapi_camelcase import CamelModel
from pydantic.fields import Field

from opvia_scripts.types.entity import AnyEntity, AnyRole
from opvia_scripts.types.result import ScriptResult


class _ScriptBase(CamelModel):
    class Config:
        arbitrary_types_allowed = True

    #: User-facing name
    title: str

    #: User-facing description
    description: str

    #: What roles the user should fill on the card
    input_roles: List[AnyRole]

    #: What roles the user should fill in the configuration menu of the card
    config_roles: List[AnyRole]


class ScriptInfo(_ScriptBase):
    """
    Information about a script, returned when info is requested
    """

    #: Entrypoint name defined in the setup file
    name: str


def setup_logger():
    logger = logging.getLogger(f"opvia_script.{str(uuid4())}")
    logger.setLevel(logging.INFO)
    return logger


class Script(_ScriptBase, ABC):

    #: A logger that can be used to emit messages to the user of the custom card.
    #: Sending messages at ``info``, ``warning``, or ``error`` level will cause these to
    #: appear live as viewable logs on the custom card.
    #: Do not set this directly as it's managed by the platform.
    logger: logging.Logger = Field(
        default_factory=lambda: setup_logger(),
        exclude=True,
    )

    @abstractmethod
    def run(self, entities: Dict[str, AnyEntity]) -> List[ScriptResult]:
        """
        Given a mapping from entity role name to the corresponding Entity,
        perform some action and return a list of instructions to Opvia.
        """
