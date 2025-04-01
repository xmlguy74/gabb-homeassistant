"""Posterfy sensor platform."""
import logging
import datetime
import aiohttp
from typing import Any, Callable, Dict, Optional
import voluptuous as vol
import datetime

from homeassistant.components.binary_sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
)
from homeassistant.core import HomeAssistant

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=300)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)

    trackers = []
    _LOGGER.info("Found config for gabb " + config[CONF_NAME])
    
    trackers.append(
        GabbDevice(
            "Abby", session, config[CONF_USERNAME], config[CONF_PASSWORD], "1234",
        )
    )

    if len(trackers) > 0:
        async_add_entities(trackers, update_before_add=True)


class GabbDevice(Entity):
    """Representation of a Gabb device tracker."""

    def __init__(self,
        name: str,
        session: aiohttp.client.ClientSession,
        username: str,
        password: str,
        device_id: str
    ):
        super().__init__()
        self.session = session
        self.username = username
        self.password = password
        self.attrs: Dict[str, Any] = {}
        self._name = name
        self._device_id = device_id
        self._state = False
        self._available = True
        

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name
    
    @property
    def unique_id(self) -> str:
        """Returns the unique ID of the entity."""
        return self._device_id
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    # @property
    # def icon(self):
    #     return "mdi:map-marker-outline"

    @property
    def state(self) -> str:
        """Returns the unique ID of the entity."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    async def async_update(self):
        try:
            # Set state to something meaningful? new date?
            self._state = True
            self.attrs["latitude"] = "35.649654"
            self.attrs["longitude"] = "-78.883079"
            self.attrs["gps_accuracy"] = 0
            self._available = True
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data from gabb.")