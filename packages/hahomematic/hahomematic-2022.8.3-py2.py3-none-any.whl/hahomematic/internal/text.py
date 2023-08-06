"""Module for entities implemented using text."""
from __future__ import annotations

import logging
from typing import Any

from hahomematic.const import HmPlatform
import hahomematic.device as hm_device
from hahomematic.entity import GenericEntity

_LOGGER = logging.getLogger(__name__)


class HmText(GenericEntity[str]):
    """
    Implementation of a text.
    This is an internal default platform that gets automatically generated.
    """

    def __init__(
        self,
        device: hm_device.HmDevice,
        unique_identifier: str,
        channel_address: str,
        paramset_key: str,
        parameter: str,
        parameter_data: dict[str, Any],
    ):
        super().__init__(
            device=device,
            unique_identifier=unique_identifier,
            channel_address=channel_address,
            paramset_key=paramset_key,
            parameter=parameter,
            parameter_data=parameter_data,
            platform=HmPlatform.TEXT,
        )

    async def send_value(self, value: str | None) -> None:
        """Set the value of the entity."""
        await super().send_value(value)
