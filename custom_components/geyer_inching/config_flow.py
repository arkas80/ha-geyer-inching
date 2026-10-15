"""Choose an existing Tuya switch. No credentials or local keys required."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .source import resolve
from .codec import decode


class ConfigFlow(config_entries.ConfigFlow, domain="geyer_inching"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                _, device = resolve(self.hass, user_input["source_entity"])
                decode(device.status["switch_inching"])
            except (ValueError, TypeError, AttributeError):
                errors["base"] = "unsupported"
            else:
                await self.async_set_unique_id(device.id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Geyer Inching", data=user_input)
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required("source_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch", integration="tuya"))
        }), errors=errors)
