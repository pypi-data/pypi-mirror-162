from . import EcoDevicesRT2
from .const import RESPONSE_ENTRY
from .const import RESPONSE_SUCCESS_VALUE
from .const import RT2_API
from .exceptions import (
    EcoDevicesRT2RequestError,
)


class X4FP:
    """Class representing the X4FP"""

    def __init__(self, ecort2: EcoDevicesRT2, module_id: int, zone_id: int) -> None:
        self._ecort2 = ecort2
        self._module_id = module_id
        self._zone_id = zone_id
        self._fp_value = (self._module_id - 1) * 4 + self._zone_id

        self._value_get_link = RT2_API["x4fp"]["value"]["get"]["link"]
        self._value_get_entry = RT2_API["x4fp"]["value"]["get"]["entry"] % (
            self._module_id,
            self._zone_id,
        )
        self._value_set_link = RT2_API["x4fp"]["value"]["set"]["link"]
        self._value_get_convert = RT2_API["x4fp"]["value"]["get"]["convert"]

    def get_mode(self, cached_ms: int = None) -> int:
        """Return the current X4FP mode."""
        response = self._ecort2.get(self._value_get_link, cached_ms=cached_ms)
        return (
            self._value_get_convert[response[self._value_get_entry]]
            if (self._value_get_entry) in response
            else None
        )

    @property
    def mode(self) -> int:
        return self.get_mode()

    @mode.setter
    def mode(self, value: int):
        """Change the current X4FP mode."""
        response = self._ecort2.get(self._value_set_link % (self._fp_value, value))
        if response[RESPONSE_ENTRY] != RESPONSE_SUCCESS_VALUE or value > 5:
            raise EcoDevicesRT2RequestError(
                "Ecodevices RT2 API error, unable to change the mode for FP extention %d, Zone %d to %d"
                % (self._module_id, self._zone_id, value)
            )
