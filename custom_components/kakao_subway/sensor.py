"""Seoul Subway sensor component for Home Assistant."""
import asyncio
import logging
from datetime import timedelta
import aiohttp
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_STATION_ID = "station_id"
DEFAULT_NAME = "Seoul Subway"
SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STATION_ID): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Seoul Subway sensor."""
    station_id = config[CONF_STATION_ID]
    name = config[CONF_NAME]

    session = async_get_clientsession(hass)
    sensor = SeoulSubwaySensor(station_id, name, session)

    async_add_entities([sensor], True)

class SeoulSubwaySensor(Entity):
    """Representation of a Seoul Subway sensor."""

    def __init__(self, station_id, name, session):
        """Initialize the sensor."""
        self._station_id = station_id
        self._name = name
        self._session = session
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        """Fetch new state data for the sensor."""
        url = f"https://place.map.kakao.com/m/main/v/{self._station_id}"
        
        try:
            async with self._session.get(url) as response:
                data = await response.json()
                
                time_info = data['basicInfo']['timeInfo']
                up_info = time_info['upTimeInfo']
                down_info = time_info['downTimeInfo']

                self._state = "OK"
                self._attributes = {
                    "upbound_1_destination": up_info[0]['endStationName'],
                    "upbound_1_time_left": up_info[0]['afterMinute'],
                    "upbound_2_destination": up_info[1]['endStationName'],
                    "upbound_2_time_left": up_info[1]['afterMinute'],
                    "downbound_1_destination": down_info[0]['endStationName'],
                    "downbound_1_time_left": down_info[0]['afterMinute'],
                    "downbound_2_destination": down_info[1]['endStationName'],
                    "downbound_2_time_left": down_info[1]['afterMinute'],
                }
        except Exception as error:
            _LOGGER.error("Error fetching data: %s", error)
            self._state = "Error"
            self._attributes = {}