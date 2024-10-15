from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, _LOGGER

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Kakao Subway sensors."""
    _LOGGER.debug("Setting up Kakao Subway sensor platform...")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    station_name = entry.data["station_name"]

    sensors = [
        sensor_type(coordinator, direction, index, station_name)
        for direction in ["upbound", "downbound"]
        for index in [1, 2]
        for sensor_type in [KakaoSubwayDestinationSensor, KakaoSubwayTimeSensor]
    ]

    async_add_entities(sensors)
    _LOGGER.debug("Added Kakao Subway sensors: %s", sensors)

class KakaoSubwayBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Kakao Subway sensors."""

    def __init__(self, coordinator, direction, index, station_name, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.direction = direction
        self.index = index
        self.station_name = station_name
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{coordinator.station_id}_{direction}_{index}_{sensor_type}"
        _LOGGER.debug("Initialized sensor: %s", self._attr_unique_id)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.station_name} {self.direction.title()} #{self.index} {self.sensor_type.title()}"

class KakaoSubwayDestinationSensor(KakaoSubwayBaseSensor):
    """Representation of a Kakao Subway destination sensor."""

    def __init__(self, coordinator, direction, index, station_name):
        """Initialize the sensor."""
        super().__init__(coordinator, direction, index, station_name, "destination")

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("Getting state for destination sensor...")
        info = self.coordinator.data.get(f"{self.direction[0]}p_info", [])
        if 0 <= self.index - 1 < len(info):
            _LOGGER.debug("Destination: %s", info[self.index - 1].get("endStationName"))
            return info[self.index - 1].get("endStationName")
        _LOGGER.warning("Destination info not found for %s %s #%s", self.station_name, self.direction, self.index)
        return None

class KakaoSubwayTimeSensor(KakaoSubwayBaseSensor):
    """Representation of a Kakao Subway time sensor."""

    def __init__(self, coordinator, direction, index, station_name):
        """Initialize the sensor."""
        super().__init__(coordinator, direction, index, station_name, "time_left")

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("Getting state for time sensor...")
        info = self.coordinator.data.get(f"{self.direction[0]}p_info", [])
        if 0 <= self.index - 1 < len(info):
            _LOGGER.debug("Time left: %s", info[self.index - 1].get("afterMinute"))
            return info[self.index - 1].get("afterMinute")
        _LOGGER.warning("Time info not found for %s %s #%s", self.station_name, self.direction, self.index)
        return None