"""Resolve the chosen switch through the existing official Tuya integration."""
from homeassistant.helpers import entity_registry as er, device_registry as dr


def resolve(hass, entity_id):
    entity = er.async_get(hass).async_get(entity_id)
    if not entity or entity.platform != "tuya" or not entity.device_id:
        raise ValueError("Select a switch from the official Tuya integration")
    entry = hass.config_entries.async_get_entry(entity.config_entry_id)
    listener = getattr(entry, "runtime_data", None)
    manager = getattr(listener, "manager", None)
    device_entry = dr.async_get(hass).async_get(entity.device_id)
    if manager is None or device_entry is None:
        raise ValueError("Tuya is not ready")
    ids = [value for domain, value in device_entry.identifiers if domain == "tuya"]
    devices = [manager.device_map[value] for value in ids if value in manager.device_map]
    if len(devices) != 1:
        raise ValueError("Cannot resolve one Tuya device")
    device = devices[0]
    if "switch_inching" not in device.function or "switch_inching" not in device.status:
        raise ValueError("Device does not expose switch_inching")
    return manager, device
