"""Strict codec for the three-byte format observed on this ER120WM."""
import base64
import math


def decode(value):
    if not isinstance(value, str):
        raise ValueError("Missing inching value")
    raw = base64.b64decode(value, validate=True)
    if len(raw) != 3 or raw[0] != 1:
        raise ValueError("Unsupported or disabled inching format; enable in Smart Life")
    return int.from_bytes(raw[1:], "big") / 60


def encode(minutes, current):
    decode(current)  # Never overwrite unknown flags or a disabled configuration.
    minutes = float(minutes)
    if not math.isfinite(minutes) or not minutes.is_integer() or not 1 <= minutes <= 99:
        raise ValueError("Select a whole number from 1 to 99 minutes")
    return base64.b64encode(bytes([1]) + (int(minutes) * 60).to_bytes(2, "big")).decode()