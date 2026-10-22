## Unreleased — 2026-10-22

- Separate experimental Tuya Local example for ER120WM, with fixed 5–40 minute DP44 mappings and per-day scheduling.
- User verified local On/Off, local change 6→7 minutes, and automatic shutdown after 7 minutes. Full range, new weekly schedule and disconnected-Internet use remain unverified on hardware.
- Cloud integration code and version are unchanged.

# Changelog / Ιστορικό αλλαγών

## 2026-10-15 — ER120WM package and documentation update

### English
- Documented user-reported HACS installation and ER120WM checks, including outstanding full Bath-cycle verification.
- Optional package restores Short while idle, checks after startup and every minute, and coordinates restoration with HA starts. Restoration requires HA/Tuya connectivity.
- Added a built-in-card dashboard example. HACS does not install or update the package or card.
- Integration Python code is unchanged; manifest version remains 0.1.0. This package/documentation update is not a new integration release.

### Ελληνικά
- Καταγράφηκαν η εγκατάσταση HACS και οι δοκιμές ER120WM που επιβεβαίωσε ο χρήστης. Εκκρεμεί ο πλήρης κύκλος Μπάνιο.
- Το προαιρετικό package επαναφέρει το Σύντομο όταν είναι σβηστός, με έλεγχο στην εκκίνηση και ανά λεπτό, χωρίς ταυτόχρονη αλλαγή χρόνου από εκκίνηση HA. Απαιτεί επικοινωνία HA/Tuya.
- Προστέθηκε παράδειγμα κάρτας. Package και κάρτα ενημερώνονται ξεχωριστά από το HACS.
- Ο κώδικας Python της ενσωμάτωσης δεν άλλαξε· το manifest παραμένει 0.1.0. Δεν είναι νέα έκδοση της ενσωμάτωσης.
