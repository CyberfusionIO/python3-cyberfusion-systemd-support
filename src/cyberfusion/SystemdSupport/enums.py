"""Unit state enums.

See: https://www.freedesktop.org/software/systemd/man/latest/systemctl.html#is-active%20PATTERN%E2%80%A6
"""

from enum import StrEnum


class ActiveState(StrEnum):
    """Possible values of a unit's ActiveState property."""

    ACTIVE = "active"
    RELOADING = "reloading"
    INACTIVE = "inactive"
    FAILED = "failed"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"
    MAINTENANCE = "maintenance"


class SubState(StrEnum):
    """Possible values of a unit's SubState property.

    Union of sub-states across all unit types (service, socket, mount, device,
    target, automount, timer, path, slice, scope).
    """

    ABANDONED = "abandoned"
    ACTIVE = "active"
    AUTO_RESTART = "auto-restart"
    CLEANING = "cleaning"
    CONDITION = "condition"
    DEAD = "dead"
    ELAPSED = "elapsed"
    EXITED = "exited"
    FAILED = "failed"
    FINAL_SIGKILL = "final-sigkill"
    FINAL_SIGTERM = "final-sigterm"
    FINAL_WATCHDOG = "final-watchdog"
    LISTENING = "listening"
    MOUNTED = "mounted"
    MOUNTING = "mounting"
    MOUNTING_DONE = "mounting-done"
    PLUGGED = "plugged"
    REFRESH_EXTENSIONS = "refresh-extensions"
    RELOAD = "reload"
    RELOAD_NOTIFY = "reload-notify"
    RELOAD_SIGNAL = "reload-signal"
    REMOUNTING = "remounting"
    REMOUNTING_SIGKILL = "remounting-sigkill"
    REMOUNTING_SIGTERM = "remounting-sigterm"
    RUNNING = "running"
    START = "start"
    START_CHOWN = "start-chown"
    START_POST = "start-post"
    START_PRE = "start-pre"
    STOP = "stop"
    STOP_POST = "stop-post"
    STOP_PRE = "stop-pre"
    STOP_PRE_SIGKILL = "stop-pre-sigkill"
    STOP_PRE_SIGTERM = "stop-pre-sigterm"
    STOP_SIGKILL = "stop-sigkill"
    STOP_SIGTERM = "stop-sigterm"
    STOP_WATCHDOG = "stop-watchdog"
    TENTATIVE = "tentative"
    UNMOUNTING = "unmounting"
    UNMOUNTING_SIGKILL = "unmounting-sigkill"
    UNMOUNTING_SIGTERM = "unmounting-sigterm"
    WAITING = "waiting"
