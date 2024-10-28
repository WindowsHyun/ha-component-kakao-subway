from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, _LOGGER

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Kakao Subway sensors."""
    _LOGGER.debug("Setting up Kakao Subway sensor platform...")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    station_name = entry.data["station_name"]
    station_id = entry.data["station_id"]

    sensors = [
        sensor_type(coordinator, direction, index, station_name, station_id)
        for direction in ["up", "down"]
        for index in [1, 2]
        for sensor_type in [KakaoSubwayDestinationSensor, KakaoSubwayTimeSensor]
    ]

    async_add_entities(sensors)
    _LOGGER.debug("Added Kakao Subway sensors: %s", sensors)

class KakaoSubwayBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Kakao Subway sensors."""

    def __init__(self, coordinator, direction, index, station_name, station_id, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.direction = direction
        self.index = index
        self.station_name = station_name
        self.station_id = station_id
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{coordinator.station_id}_{direction}_{index}_{sensor_type}"
        _LOGGER.debug("Initialized sensor: %s", self._attr_unique_id)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.station_name} {self.direction.title()}bound #{self.index} {self.sensor_type.title()}"
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.station_id)},
            name=self.station_name,
        )

class KakaoSubwayDestinationSensor(KakaoSubwayBaseSensor):
    """Representation of a Kakao Subway destination sensor."""

    def __init__(self, coordinator, direction, index, station_name, station_id):
        """Initialize the sensor."""
        super().__init__(coordinator, direction, index, station_name, station_id, "destination")

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("Getting state for destination sensor: %s", self._attr_unique_id)
        info = self.coordinator.data.get(f"{self.direction}_info", [])
        if 0 <= self.index - 1 < len(info):
            destination = info[self.index - 1].get("endStationName")
            _LOGGER.debug("Destination: %s", destination)
            return destination
        _LOGGER.warning("Destination info not found for %s", self._attr_unique_id)
        return None

class KakaoSubwayTimeSensor(KakaoSubwayBaseSensor):
    """Representation of a Kakao Subway time sensor."""

    def __init__(self, coordinator, direction, index, station_name, station_id):
        """Initialize the sensor."""
        super().__init__(coordinator, direction, index, station_name, station_id, "time_left")

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("Getting state for time sensor: %s", self._attr_unique_id)
        info = self.coordinator.data.get(f"{self.direction}_info", [])
        if 0 <= self.index - 1 < len(info):
            time_left = info[self.index - 1].get("afterMinute")
            _LOGGER.debug("Time left: %s", time_left)
            return time_left
        _LOGGER.warning("Time info not found for %s", self._attr_unique_id)
        return None