from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Kakao Subway sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = []
    
    for direction in ["upbound", "downbound"]:
        for index in [1, 2]:
            sensors.extend([
                SeoulSubwayDestinationSensor(coordinator, direction, index),
                SeoulSubwayTimeSensor(coordinator, direction, index)
            ])
    
    async_add_entities(sensors)

class SeoulSubwayBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Kakao Subway sensors."""

    def __init__(self, coordinator, direction, index, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.direction = direction
        self.index = index
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{coordinator.station_id}_{direction}_{index}_{sensor_type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Kakao Subway {self.direction.capitalize()} {self.index} {self.sensor_type.capitalize()}"

class SeoulSubwayDestinationSensor(SeoulSubwayBaseSensor):
    """Representation of a Kakao Subway destination sensor."""

    def __init__(self, coordinator, direction, index):
        """Initialize the sensor."""
        super().__init__(coordinator, direction, index, "destination")

    @property
    def state(self):
        """Return the state of the sensor."""
        info = self.coordinator.data[f"{self.direction[0]}p_info"][self.index - 1]
        return info["endStationName"]

class SeoulSubwayTimeSensor(SeoulSubwayBaseSensor):
    """Representation of a Kakao Subway time sensor."""

    def __init__(self, coordinator, direction, index):
        """Initialize the sensor."""
        super().__init__(coordinator, direction, index, "time_left")

    @property
    def state(self):
        """Return the state of the sensor."""
        info = self.coordinator.data[f"{self.direction[0]}p_info"][self.index - 1]
        return info["afterMinute"]