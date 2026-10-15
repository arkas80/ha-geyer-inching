# Geyer Inching for Home Assistant

[Ελληνικές οδηγίες](README.el.md) · English

A custom integration that reads and changes the existing Inching duration of a compatible Geyer/Tuya water-heater switch through Home Assistant's official Tuya integration. Includes an optional package for independently saved **Short** and **Bath** durations.

## Scope and status

- Developed around a Geyer ER120WM and the observed `switch_inching` payload format. Compatibility with other models is not established.
- The number entity advertises 5–40 whole minutes, and the optional package enforces that range. The preserved low-level encoder accepts 1–99 minutes; it does not itself enforce the narrower UI range. The integration refuses duration writes while the relay is on or the device is offline.
- No new Tuya login or local key is requested. It reuses the official Tuya integration's internal runtime interfaces, which may change between HA releases.
- This is not an official Geyer, Tuya or Home Assistant integration. Offline tests are provided; they are not a substitute for checking real-device shutdown.
- The source is preserved from a local folder named `geyer-inching-0.2.0`; its original manifest still declares `0.1.0`. This naming mismatch is intentional documentation of the existing source, not a claim that a verified 0.2.0 release exists. Dashboard version numbers are separate.
- The current implementation targets one configured device and sets the entity ID `number.geyer_inching_minutes`. Verify the actual ID in HA; multiple-device support has not been validated.

## Install the integration

1. Back up your Home Assistant configuration.
2. Copy `custom_components/geyer_inching` into `/config/custom_components/geyer_inching`. Do not replace the entire `custom_components` folder. File Editor may show `/homeassistant` instead of `/config`.
3. Restart HA. Under **Settings → Devices & services → Add integration**, select **Geyer Inching**.
4. Select the existing switch from the **official Tuya integration**. An entity supplied only by LocalTuya is not supported by this code.
5. Check the newly created number entity. With the relay OFF, change a duration and verify the same value in the device's app and the real automatic shutdown on a supervised cycle.

### HACS custom repository

Repository metadata is prepared for HACS; installation on a live HA instance still needs verification. This is not a listing in the default HACS catalog.

1. Back up HA, including your existing `custom_components/geyer_inching` folder if installed manually.
2. Open HACS, select the three-dot menu, then **Custom repositories**.
3. Enter `https://github.com/arkas80/ha-geyer-inching`, choose **Integration**, and select **Add**.
4. Find **Geyer Inching**, open it and select **Download**. Use the default branch if no release is offered.
5. Restart Home Assistant when the water heater is off. If Geyer Inching was already configured, keep that integration entry; do not delete it or add a duplicate. Check that the existing number entity remains available.
6. For a new installation, add **Geyer Inching** under Settings → Devices & services and select your official Tuya switch.

HACS installs only the integration. The optional package below must be installed separately; it does not replace your dashboard. If HACS reports an error, retain the working manual installation and record the exact message.


### Confirmation behavior

The number implementation temporarily publishes an optimistic value while sending the command, but the service call continues waiting for the Tuya status payload. If acknowledgement is not received, it restores the reported value and raises an error. Merely seeing the number change in the UI is not proof of device acknowledgement. The supplied package waits for the service call to finish before starting the relay.

## Optional Short / Bath package

The package belongs in **`packages/`**, not in `custom_components/geyer_inching/`.

1. Open `examples/packages/spiti_boiler.yaml` and replace **every** occurrence of `switch.your_water_heater` with your actual switch entity ID. If necessary, also replace `number.geyer_inching_minutes` with your number entity ID.
2. Copy the edited file to `/config/packages/spiti_boiler.yaml`.
3. If packages are not already configured, merge this into `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Do not duplicate an existing `homeassistant:` or `packages:` key. This example is for `!include_dir_named`, not `!include_dir_merge_named`. Existing `automation: !include automations.yaml` and `script: !include scripts.yaml` can remain.

4. Check the configuration and restart HA.
5. Set **both** durations before first use: `input_number.spiti_boiler_short_minutes` and `input_number.spiti_boiler_bath_minutes`. With no restored state they start at the minimum (5 minutes); choose your own durations. No `initial` is set on these helpers, so later values can be restored.
6. Call `script.spiti_boiler_start` with `program: short` or `program: bath`. Call `script.spiti_boiler_stop` to cancel a pending start and turn the relay off.

Example action (only run when you intend to start the heater):

```yaml
action: script.spiti_boiler_start
data:
  program: short
```

The start script is `single`, validates the range and OFF state, waits for duration setting to complete, records the cycle duration, and then switches on. Service errors or confirmation timeouts stop the sequence. The device's existing Inching remains responsible for automatic shutdown; the package does not replace it with an HA delay and does not restart the heater automatically.

### Existing timers and estimated progress

Inspect existing automations before use. An older automation that starts a timer using a different slider can shut down Bath early. Preserve its configuration; after verifying device-side Inching, disable only the conflicting automation while the heater is OFF and cancel its old timer. Do not disable other automations indiscriminately.

The package creates `sensor.spiti_boiler_remaining_estimated`, an **estimated** remaining duration updated every 10 seconds. It derives from a captured deadline, not a device countdown or water temperature. It becomes unavailable for an already-running cycle after an HA restart. External OFF→ON starts are recorded using the reported Inching duration when available. A full personalized household dashboard is not included.

## Offline tests

```sh
python test_offline.py
```

These standard-library tests cover payload encoding, supported ranges, rejection while on/offline, acknowledgement and rollback. They do not access a network or switch a real relay.

## Rollback

With the heater OFF, restore your previous dashboard and automation setup. Remove the optional package, validate and restart if you no longer want its helpers/scripts. The original integration can remain. Removing either component does not reset the Inching value stored on the device.

## Reporting problems

Include HA version, device model, integration version, and sanitized error logs. Do not include credentials, tokens, Tuya device IDs, MAC addresses, or full HA configuration exports. Compatibility with a newer HA version should be tested before relying on it.

## License

No open-source license has been selected yet. A public repository alone does not grant an open-source redistribution license. A license can be added by the owner before a public release.

References: [HA packages](https://www.home-assistant.io/docs/configuration/packages/) · [HA scripts](https://www.home-assistant.io/docs/scripts/)
