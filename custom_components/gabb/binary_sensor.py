"""Posterfy sensor platform."""
import logging
import datetime
from typing import Any, Callable, Dict, Optional
import voluptuous as vol
import datetime

from types import SimpleNamespace
from homeassistant.components.binary_sensor import PLATFORM_SCHEMA
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

from gabb import GabbClient

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
    }
)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    trackers = []
    _LOGGER.info("Found config for gabb " + config[CONF_NAME])
    
    # Create a GabbClient instance and get the devices
    gabb_client = GabbClient(config[CONF_USERNAME], config[CONF_PASSWORD])
    map = gabb_client.get_map().json(object_hook=lambda d: SimpleNamespace(**d))

    if map.status != 200:
        raise Exception("Error getting map data from gabb. " + map.message)
    
    # Loop through the devices and create a GabbDevice for each one
    for device in map.data.Devices:
        _LOGGER.info("Found device " + device.id)
        trackers.append(
            GabbDevice(
                device.firstName, config[CONF_USERNAME], config[CONF_PASSWORD], device.id,
            )
        )

    if len(trackers) > 0:
        add_entities(trackers, update_before_add=True)


class GabbDevice(Entity):
    """Representation of a Gabb device tracker."""

    def __init__(self,
        name: str,
        username: str,
        password: str,
        device_id: str
    ):
        super().__init__()
        self.attrs: Dict[str, Any] = {}

        self._username = username
        self._password = password
        self._name = name
        self._device_id = device_id
        self._state = False
        self._available = True
        

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name + "_" + self._device_id
    
    @property
    def unique_id(self) -> str:
        """Returns the unique ID of the entity."""
        return self._name + "_" + self._device_id
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> str:
        """Returns the unique ID of the entity."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    def update(self):
        try:
            gabb_client = GabbClient(self.username, self.password)
            map = gabb_client.get_map().json(object_hook=lambda d: SimpleNamespace(**d))
            if map.status != 200:
                _LOGGER.exception("Error getting map data from gabb. " + map.message)
            else:                
                # Loop through the devices and create a GabbDevice for each one
                device = next((d for d in map.data.Devices if d.id == self._device_id), None)                
                if device is None:
                    _LOGGER.error("Device not found in map data.")
                    self._available = False
                else:                    
                    _LOGGER.info("Found device " + device.id)
                    self._state = True
                    self.attrs["source_type"] = "gps"                        
                    self.attrs["latitude"] = device.latitude
                    self.attrs["longitude"] = device.longitude
                    self.attrs["gps_accuracy"] = 0
                    self.attrs["battery_level"] = device.batteryLevel
                    self._available = True
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data from gabb.")