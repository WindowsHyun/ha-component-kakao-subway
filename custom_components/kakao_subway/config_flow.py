from typing import Any, Dict, Optional
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kakao Subway."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", 
                data_schema=vol.Schema({
                    vol.Required("station_id"): str,
                    vol.Required("station_name"): str
                })
            )

        errors = {}

        try:
            # Here you could add validation for the station_id and station_name if needed
            pass
        except Exception:  # pylint: disable=broad-except
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=f"{user_input['station_name']} ({user_input['station_id']})", data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required("station_id"): str,
                vol.Required("station_name"): str
            }), 
            errors=errors
        )