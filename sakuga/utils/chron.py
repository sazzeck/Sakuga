import datetime as dt
import time


def sys_time() -> str:
    return time.strftime("%H:%M:%S")


def utc_time() -> str:
    return dt.datetime.utcnow().strftime("%H:%M:%S")


def short_date(obj: dt.datetime) -> str:
    return obj.strftime("%d/%m/%y")


def short_date_and_time(obj: dt.datetime) -> str:
    return obj.strftime("%d/%m/%y %H:%M:%S")


def long_date(obj: dt.datetime) -> str:
    return obj.strftime("%d %b %Y")


def long_date_and_time(obj: dt.datetime) -> str:
    return obj.strftime("%d %b %Y at %H:%M:%S")


def short_delta(delta: dt.timedelta, ms: bool = False) -> str:
    parts = []

    if delta.days != 0:
        parts.append(f"{delta.days:,}d")

    if (h := delta.seconds // 3600) != 0:
        parts.append(f"{h}h")

    if (m := delta.seconds // 60 - (60 * h)) != 0:
        parts.append(f"{m}m")

    if (s := delta.seconds - (60 * m) - (3600 * h)) != 0 or not parts:
        if ms:
            milli = round(delta.microseconds / 1000)
            parts.append(f"{s}.{milli}s")
        else:
            parts.append(f"{s}s")

    return ", ".join(parts)


def from_iso(stamp: str) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(stamp)
    except TypeError:
        # In case there's no records:
        return dt.datetime.min


def to_iso(obj: dt.datetime) -> str:
    return obj.isoformat(" ")
