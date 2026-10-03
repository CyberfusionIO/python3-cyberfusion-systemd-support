"""Classes for systemd units."""

import glob
import json
import os
import subprocess
from functools import wraps
from typing import Callable, List, Optional, TypeVar, cast

from cyberfusion.SystemdSupport._constants import SYSTEMCTL_BIN
from cyberfusion.SystemdSupport.exceptions import (
    UnexpectedActiveStateError,
    UnexpectedSubStateError,
)
from cyberfusion.SystemdSupport.manager import SystemdManager
from cyberfusion.SystemdSupport.enums import ActiveState, SubState

F = TypeVar("F", bound=Callable[..., None])


BASE_DIRECTORY_SYSTEMD_UNITS = os.path.join(os.path.sep, "etc", "systemd", "system")

SYSTEMD_RUN_BIN = os.path.join(os.path.sep, "bin", "systemd-run")


def reload_manager(f: F) -> F:
    """Reload manager configuration if needed.."""

    @wraps(f)
    def wrapper(
        self: "Unit",
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        if self.needs_reload:
            SystemdManager.daemon_reload()

        f(self, *args, **kwargs)

    return cast(F, wrapper)


class Unit:
    """Represents unit."""

    SUFFIX_SERVICE = "service"

    def __init__(self, name: str) -> None:
        """Set attributes."""
        self.name = name

    def get_property(self, name: str) -> Optional[str]:
        """Get unit property from systemd."""
        output = subprocess.run(
            [SYSTEMCTL_BIN, "-P", name, "show", self.name],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.rstrip()

        if output == "":
            return None

        return output

    @property
    def drop_in_directory(self) -> str:
        """Get path to drop-in directory."""
        return self.get_drop_in_directory(self.name)

    @property
    def needs_reload(self) -> bool:
        """Get if manager needs to be reloaded for unit."""

        # systemd itself decides that daemon-reload is needed

        if self.get_property("NeedDaemonReload") == "yes":
            return True

        # Drop-in directory was added after the latest daemon-reload (systemd
        # does not detect it itself in that case, see: https://github.com/systemd/systemd/issues/31752)

        if (
            os.path.isdir(self.drop_in_directory)
            and glob.glob(os.path.join(self.drop_in_directory, "*.conf"))
            and self.get_property("DropInPaths") is None
        ):
            return True

        return False

    def disable(self) -> None:
        """Disable unit."""
        if not self.is_enabled:
            return

        subprocess.run([SYSTEMCTL_BIN, "disable", self.name], check=True)

    def enable(self) -> None:
        """Enable unit."""
        if self.is_enabled:
            return

        subprocess.run([SYSTEMCTL_BIN, "enable", self.name], check=True)

    @reload_manager
    def stop(self) -> None:
        """Stop unit."""
        if not self.is_active:
            return

        subprocess.run([SYSTEMCTL_BIN, "stop", self.name], check=True)

    @reload_manager
    def restart(self) -> None:
        """Restart unit."""
        subprocess.run([SYSTEMCTL_BIN, "restart", self.name], check=True)

    @reload_manager
    def start(self) -> None:
        """Start unit."""
        if self.is_active:
            return

        subprocess.run([SYSTEMCTL_BIN, "start", self.name], check=True)

    @reload_manager
    def reload(self) -> None:
        """Reload unit."""
        subprocess.run([SYSTEMCTL_BIN, "reload", self.name], check=True)

    @property
    def is_active(self) -> bool:
        """Get if unit is active."""
        try:
            subprocess.run(
                [SYSTEMCTL_BIN, "is-active", "--quiet", self.name], check=True
            )
        except subprocess.CalledProcessError:
            return False

        return True

    @property
    def is_enabled(self) -> bool:
        """Get if unit is enabled."""
        try:
            subprocess.run(
                [SYSTEMCTL_BIN, "is-enabled", "--quiet", self.name], check=True
            )
        except subprocess.CalledProcessError:
            return False

        return True

    @property
    def is_failed(self) -> bool:
        """Get if unit is enabled."""
        try:
            subprocess.run(
                [SYSTEMCTL_BIN, "is-failed", "--quiet", self.name], check=True
            )
        except subprocess.CalledProcessError:
            return False

        return True

    @staticmethod
    def get_drop_in_directory(unit_name: str) -> str:
        """Get unit override directory."""
        return Unit.get_unit_file(unit_name) + ".d"

    @staticmethod
    def get_unit_file(unit_name: str) -> str:
        """Get unit file."""
        return os.path.join(BASE_DIRECTORY_SYSTEMD_UNITS, unit_name)

    @staticmethod
    def remove_unit_type(unit_name: str) -> str:
        """Remove unit type from unit name.

        E.g.: `firewall.service` -> `firewall`
        """
        return unit_name.rsplit(".", 1)[0]

    @staticmethod
    def add_unit_type(unit_name: str, unit_type: str) -> str:
        """Add unit type to unit name.

        E.g.: `firewall` -> `firewall.service`
        """
        return unit_name + "." + unit_type


class TransientUnit:
    """Represents transient unit created via systemd-run."""

    def __init__(self, unit: Unit) -> None:
        """Set attributes."""
        self.unit = unit

    @classmethod
    def run(cls, name: str, command: List[str]) -> "TransientUnit":
        """Start transient unit and return an instance wrapping the created unit."""
        output = subprocess.run(
            [
                SYSTEMD_RUN_BIN,
                "--json=short",
                f"--unit={name}",
                "--remain-after-exit",
                *command,
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout

        return cls(Unit(json.loads(output)["unit"]))

    @classmethod
    def run_sync(
        cls,
        name: str,
        command: List[str],
        *,
        properties: dict[str, str] | None = None,
        input_: str | None = None,
    ) -> str:
        """Start transient unit, wait for it to finish, and return stdout."""
        arguments = [
            SYSTEMD_RUN_BIN,
            f"--unit={name}",
            # "Wait for the transient service to terminate"
            "--wait",
            # "Unload the transient unit after it completed, even if it failed"
            "--collect",
            # "standard input, output, and error of the transient service are inherited from the systemd-run command itself"
            # Needed to pass stdin
            "--pipe",
        ]

        if properties:
            for property_name, property_value in properties.items():
                arguments.append(f"--property={property_name}={property_value}")

        arguments.extend(command)

        output = subprocess.run(
            arguments, check=True, stdout=subprocess.PIPE, text=True, input=input_
        ).stdout

        return output

    def clean_up(self) -> None:
        """Stop unit if active, or reset it if failed."""
        sub_state = self.unit.get_property("SubState")

        # A finished --remain-after-exit unit is either `exited` (success) or
        # `failed`. Any other value means the unit is still `running`, or in
        # some other state we don't handle — bail out so it can be debugged
        # manually rather than silently tearing it down.

        if sub_state not in (SubState.EXITED, SubState.FAILED):
            raise UnexpectedSubStateError(self.unit.name, sub_state)

        active_state = self.unit.get_property("ActiveState")

        if active_state == ActiveState.ACTIVE:
            subprocess.run([SYSTEMCTL_BIN, "stop", self.unit.name], check=True)
        elif active_state == ActiveState.FAILED:
            subprocess.run([SYSTEMCTL_BIN, "reset-failed", self.unit.name], check=True)
        else:
            raise UnexpectedActiveStateError(self.unit.name, active_state)
