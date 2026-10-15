"""Offline behavior tests. Does not connect to HA, Tuya or the heater."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).parent / "custom_components" / "geyer_inching"
pkg = types.ModuleType("geyer_test")
pkg.__path__ = [str(ROOT)]
sys.modules["geyer_test"] = pkg
from geyer_test.codec import decode, encode


class CodecTests(unittest.TestCase):
    def test_real_diagnostics(self):
        self.assertEqual(decode("AQHg"), 8)
        self.assertEqual(decode("AQIc"), 9)
        self.assertEqual(encode(8, "AQIc"), "AQHg")
        self.assertEqual(encode(9, "AQHg"), "AQIc")

    def test_allowed_range(self):
        for minutes in range(1, 100):
            self.assertEqual(decode(encode(minutes, "AQHg")), minutes)
        for value in [0, 100, 8.5, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                encode(value, "AQHg")

    def test_unknown_or_disabled_format(self):
        for raw in ["", "AAHg", "AQ==", "AQHgAAAA", "???"]:
            with self.assertRaises(ValueError):
                encode(9, raw)


# Stub the small HA surface to test command behavior independently.
number_stub = types.ModuleType("homeassistant.components.number")
number_stub.NumberEntity = type("NumberEntity", (), {"async_write_ha_state": lambda self: None})
number_stub.NumberMode = types.SimpleNamespace(BOX="box")
exc_stub = types.ModuleType("homeassistant.exceptions")
exc_stub.HomeAssistantError = type("HomeAssistantError", (Exception,), {})
source_stub = types.ModuleType("geyer_test.source")
source_stub.resolve = lambda *args: None
sys.modules["homeassistant.components.number"] = number_stub
sys.modules["homeassistant.exceptions"] = exc_stub
sys.modules["geyer_test.source"] = source_stub
from geyer_test import number


class WriteTests(unittest.IsolatedAsyncioTestCase):
    def setup_entity(self, on=False, online=True, ack=True):
        device = types.SimpleNamespace(id="test", online=online,
            status={"switch_1": on, "switch_inching": "AQHg"})
        calls = []
        def send(device_id, commands):
            calls.append(commands)
            if ack:
                device.status["switch_inching"] = commands[0]["value"]
        manager = types.SimpleNamespace(send_commands=send)
        entity = number.GeyerInching(types.SimpleNamespace(
            data={"source_entity": "switch.test"}, unique_id="test"))
        async def execute(fn, *args):
            return fn(*args)
        entity.hass = types.SimpleNamespace(async_add_executor_job=execute)
        return entity, device, manager, calls

    async def test_read_never_sends(self):
        entity, device, manager, calls = self.setup_entity()
        with patch.object(number, "resolve", return_value=(manager, device)):
            await entity.async_update()
            device.status["switch_inching"] = "AQIc"
            await entity.async_update()
        self.assertEqual(entity._attr_native_value, 9)
        self.assertEqual(calls, [])

    async def test_write_only_inching_and_confirm(self):
        entity, device, manager, calls = self.setup_entity()
        with patch.object(number, "resolve", return_value=(manager, device)), patch.object(number.asyncio, "sleep", new=AsyncMock()):
            await entity.async_set_native_value(9)
        self.assertEqual(calls, [[{"code": "switch_inching", "value": "AQIc"}]])
        self.assertFalse(device.status["switch_1"])
        self.assertEqual(entity._attr_native_value, 9)

    async def test_on_or_offline_rejected(self):
        for on, online in [(True, True), (False, False), (None, True)]:
            entity, device, manager, calls = self.setup_entity(on, online)
            with patch.object(number, "resolve", return_value=(manager, device)):
                with self.assertRaises(exc_stub.HomeAssistantError):
                    await entity.async_set_native_value(9)
            self.assertEqual(calls, [])

    async def test_missing_ack_restores_reported_value(self):
        entity, device, manager, calls = self.setup_entity(ack=False)
        with patch.object(number, "resolve", return_value=(manager, device)), patch.object(number.asyncio, "sleep", new=AsyncMock()):
            await entity.async_update()
            with self.assertRaises(exc_stub.HomeAssistantError):
                await entity.async_set_native_value(9)
        self.assertEqual(entity._attr_native_value, 8)
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
