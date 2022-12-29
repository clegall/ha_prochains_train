import asyncio
import logging

import aiohttp
import async_timeout
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_API_KEY,
    CONF_GATEWAY,
    CONF_SCAN_INTERVAL,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

CONF_DEPARTURE_ID = "departure_id"

PLATFORM_SCHEMA = vol.All(
    cv.deprecated(CONF_GATEWAY),
    cv.deprecated(CONF_API_KEY),
    cv.deprecated(CONF_DEPARTURE_ID),
    {
        vol.Required(CONF_SCAN_INTERVAL): cv.time_period,
        vol.Required(CONF_DEPARTURE_ID): cv.string,
    },
)

async def async_setup_platform(hass, config: ConfigType, async_add_entities, discovery_info=None):
    """Set up the SNCF platform."""
    departure_id = config[CONF_DEPARTURE_ID]
    interval = config[CONF_SCAN_INTERVAL].total_seconds()

    async_add_entities([SNCFDepartureSensor(departure_id, interval)])

class SNCFDepartureSensor(Entity):
    """Representation of a SNCF departure sensor."""

    def __init__(self, departure_id, interval):
        """Initialize the sensor."""
        self._departure_id = departure_id
        self._interval = interval
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"SNCF Departure {self._departure_id}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        async with async_timeout.timeout(10):
            session = async_get_clientsession(self.hass)
            url = f"https://api.sncf.com/v1/coverage/sncf/departures?from={self._departure_id}"
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }

            async with session.get(url, headers=headers) as response:
                data = await response.json()
                departures = data["departures"]

                # Find the next departure
                for departure in departures:
                    if departure["
