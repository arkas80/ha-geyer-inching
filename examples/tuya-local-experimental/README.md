# Tuya Local — experimental ER120WM support

[Ελληνικά](README.el.md)

Tested model: Geyer ER120WM. Other models in the series may be compatible but are unverified; verify DP identifiers and payload formats before use.

Separate from the existing Cloud integration. Do not install both boiler packages: they define the same helpers, scripts and automation IDs. HACS installation of Geyer Inching does NOT install this experiment.

User-tested on one ER120WM: local relay on/off; DP44 reads at 6, 7 and 8 minutes; local change 6 to 7 minutes confirmed in device diagnostics; automatic shutoff after a 7-minute cycle. The user also tested physical-switch and Bath operation and reported restoration to the configured 7-minute Short duration. One scheduled cycle started at the configured time and stopped normally. Restoration after that scheduled cycle was not separately confirmed. The full 5–40 minute range, all weekday combinations and Internet-disconnected operation have not been tested on hardware.

Back up the installed Tuya Local profile and boiler package. Append `profile-append.yaml.txt` to the existing entities list in `custom_components/tuya_local/devices/smartplugv2_energy.yaml` only for the tested device/profile (Tuya Local 2026.9.2). Do not replace the full profile with the snippet. Generic profiles may be shared by other devices. This patch can be overwritten by updates.

Replace `switch.your_water_heater_local` and `select.your_geyer_inching_local_test` in the package with your actual entity IDs. Replace the old boiler package rather than loading both. Restart after configuration checks. Re-enable the short-duration restoration automation if disabled for testing. Keep the older timer-based shutdown automation disabled if it conflicts with hardware inching.

The weekly master and day toggles are initially off, then restore their previous values. Set time/duration before enabling. Each day has one start; already-on/busy cycles are skipped, missed starts are not replayed, and an attempted run is recorded before the command to avoid a duplicate that day. After shutdown the short duration is restored if HA and local communication work. Immediate physical restart can beat restoration. Countdown is estimated, not a device timer reading. The Local select becomes unavailable while on; a retained reported-duration sensor supports the estimate, but startup requires the actual select to be valid.

Test while present before regular use. Preserve the native safety protections. To roll back, disable scheduling, turn the heater off, restore your original package/profile/dashboard and re-enable short-duration restoration. No private diagnostics or local keys belong in GitHub.

## Dashboard helpers

Add the package helpers to your own dashboard. The master is `input_boolean.spiti_boiler_schedule_enabled`. Each DAY (mon/tue/wed/thu/fri/sat/sun) has `input_boolean.spiti_boiler_DAY_enabled`, `input_datetime.spiti_boiler_DAY_time`, and `input_number.spiti_boiler_DAY_minutes`. Use `script.spiti_boiler_start` with program short/bath and `script.spiti_boiler_stop` for manual cycles. No personal dashboard is included. When the Geyer drives only an external contactor coil, its power readings do not measure the water heater load.
