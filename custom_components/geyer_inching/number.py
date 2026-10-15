"""Read reported values; write only inching, only while the heater is off."""
import asyncio
from datetime import timedelta
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.exceptions import HomeAssistantError
from .codec import decode, encode
from .source import resolve

SCAN_INTERVAL = timedelta(seconds=5)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([GeyerInching(entry)], update_before_add=True)


class GeyerInching(NumberEntity):
    _attr_name = "Geyer Inching minutes"
    _attr_icon = "mdi:timer-cog-outline"
    _attr_native_min_value = 5
    _attr_native_max_value = 40
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "min"
    _attr_mode = NumberMode.BOX
    _attr_should_poll = True

    def __init__(self, entry):
        self._source = entry.data["source_entity"]
        self._attr_unique_id = entry.unique_id + "_inching_minutes"
        self.entity_id = "number.geyer_inching_minutes"
        self._write_lock = asyncio.Lock()

    async def async_update(self):
        # Read Tuya's MQTT-updated cache, not a new cloud request every five seconds.
        try:
            _, device = resolve(self.hass, self._source)
            self._attr_available = bool(device.online)
            self._attr_native_value = decode(device.status.get("switch_inching"))
        except (ValueError, TypeError, AttributeError):
            self._attr_available = False
            self._attr_native_value = None

    async def async_set_native_value(self, value):
        async with self._write_lock:
            try:
                manager, device = resolve(self.hass, self._source)
                if not device.online or device.status.get("switch_1") is not False:
                    raise ValueError("Close the heater and wait for Tuya to report it off before changing duration")
                payload = encode(value, device.status.get("switch_inching"))
                if payload == device.status.get("switch_inching"):
                    return

                # 🎯 OPTIMISTIC: δείξε αμέσως την τιμή, πριν την επιβεβαίωση
                self._attr_native_value = float(value)
                self.async_write_ha_state()

                await self.hass.async_add_executor_job(
                    manager.send_commands, device.id,
                    [{"code": "switch_inching", "value": payload}])

                # Επιβεβαίωση στο background (χωρίς να μπλοκάρει το UI)
                for _ in range(20):
                    await asyncio.sleep(1)
                    _, latest = resolve(self.hass, self._source)
                    if latest.status.get("switch_inching") == payload:
                        await self.async_update()
                        self.async_write_ha_state()
                        return

                # Αν δεν επιβεβαιωθεί, γύρνα στην πραγματική τιμή
                await self.async_update()
                self.async_write_ha_state()
                raise ValueError("No confirmation from Tuya. Check the Smart Life setting before trying again")
            except (ValueError, TypeError, AttributeError) as err:
                raise HomeAssistantError(str(err)) from err