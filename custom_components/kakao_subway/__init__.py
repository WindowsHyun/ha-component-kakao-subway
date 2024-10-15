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
        """API에서 데이터를 가져옵니다."""
        _LOGGER.debug("Fetching data from Kakao Subway API...")  # 로그 추가
        try:
            url = f"https://place.map.kakao.com/m/main/v/{self.station_id}"
            _LOGGER.debug("URL: %s", url)
            async with self.session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    raise Exception(f"API 요청 실패: 상태 코드 {resp.status}")
                data = await resp.json(content_type=None)  # content_type=None 추가
                _LOGGER.debug("API Response: %s", data)

                if 'basicInfo' not in data or 'timeInfo' not in data['basicInfo']:
                    raise Exception("잘못된 API 응답 구조: 필수 키가 없습니다.")

                time_info = data['basicInfo']['timeInfo']
                up_info = time_info.get('upTimeInfo', [])
                down_info = time_info.get('downTimeInfo', [])

                _LOGGER.debug("Time Info: %s", time_info)  # 로그 추가
                _LOGGER.debug("Up Info: %s", up_info)    # 로그 추가
                _LOGGER.debug("Down Info: %s", down_info)  # 로그 추가

                return {
                    "up_info": up_info,
                    "down_info": down_info
                }

        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Error communicating with API: %s", e)  # 로그 추가
            raise UpdateFailed(f"API 통신 에러: {e}")
        except json.JSONDecodeError as e:
            _LOGGER.error("Error decoding JSON response: %s", e)  # 로그 추가
            raise UpdateFailed(f"JSON 응답 디코딩 에러: {e}")
        except Exception as err:
            _LOGGER.exception("Unexpected error: %s", err)  # 로그 추가
            raise UpdateFailed(f"예상치 못한 에러: {err}")