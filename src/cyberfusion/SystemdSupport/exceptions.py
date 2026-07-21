"""Exceptions."""

from typing import Optional


class UnexpectedSubStateError(Exception):
    """Unit is in a SubState we don't know how to handle."""

    def __init__(self, unit_name: str, sub_state: Optional[str]) -> None:
        """Set attributes."""
        self.unit_name = unit_name
        self.sub_state = sub_state

        super().__init__(f"Unit {unit_name} has unexpected SubState: {sub_state}")


class UnexpectedActiveStateError(Exception):
    """Unit is in an ActiveState we don't know how to handle."""

    def __init__(self, unit_name: str, active_state: Optional[str]) -> None:
        """Set attributes."""
        self.unit_name = unit_name
        self.active_state = active_state

        super().__init__(f"Unit {unit_name} has unexpected ActiveState: {active_state}")
