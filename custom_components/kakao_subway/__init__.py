import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Kakao Subway component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Kakao Subway from a config entry."""
    session = async_get_clientsession(hass)

    coordinator = KakaoSubwayDataUpdateCoordinator(hass, session, entry)

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class KakaoSubwayDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Kakao Subway data."""

    def __init__(self, hass, session, entry):
        """Initialize."""
        self.session = session
        self.station_id = entry.data["station_id"]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            url = f"https://place.map.kakao.com/m/main/v/{self.station_id}"
            async with self.session.get(url) as resp:
                data = await resp.json()
                time_info = data['basicInfo']['timeInfo']
                return {
                    "up_info": time_info['upTimeInfo'],
                    "down_info": time_info['downTimeInfo']
                }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")