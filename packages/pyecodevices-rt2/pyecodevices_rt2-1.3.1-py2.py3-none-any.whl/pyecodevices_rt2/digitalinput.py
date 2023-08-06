from . import EcoDevicesRT2
from .const import RT2_API


class DigitalInput:
    """Class representing the DigitalInput"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        self._ecort2 = ecort2
        self._id = id
        self._value_get_link = RT2_API["digitalinput"]["status"]["get"]["link"]
        self._value_get_entry = RT2_API["digitalinput"]["status"]["get"]["entry"] % (
            self._id
        )

    def get_status(self, cached_ms: int = None) -> bool:
        """Return the current DigitalInput status."""
        response = self._ecort2.get(self._value_get_link, cached_ms=cached_ms)
        return (
            response[self._value_get_entry] == 1
            if (self._value_get_entry) in response
            else None
        )

    @property
    def status(self) -> bool:
        return self.get_status()
