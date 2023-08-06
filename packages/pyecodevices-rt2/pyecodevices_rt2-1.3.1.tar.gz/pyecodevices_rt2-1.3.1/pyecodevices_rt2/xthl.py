from . import EcoDevicesRT2
from .const import RT2_API


class XTHL:
    """Class representing the XTHL"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        self._ecort2 = ecort2
        self._id = id

        self._temperature_get_link = RT2_API["xthl"]["temperature"]["get"]["link"]
        self._temperature_get_entry = RT2_API["xthl"]["temperature"]["get"]["entry"] % (
            self._id
        )
        self._humidity_get_link = RT2_API["xthl"]["humidity"]["get"]["link"]
        self._humidity_get_entry = RT2_API["xthl"]["humidity"]["get"]["entry"] % (
            self._id
        )
        self._luminosity_get_link = RT2_API["xthl"]["luminosity"]["get"]["link"]
        self._luminosity_get_entry = RT2_API["xthl"]["luminosity"]["get"]["entry"] % (
            self._id
        )

    def get_temperature(self, cached_ms: int = None) -> bool:
        """Return the current XTHL temperature."""
        response = self._ecort2.get(self._temperature_get_link, cached_ms=cached_ms)
        return (
            response[self._temperature_get_entry]
            if (self._temperature_get_entry) in response
            else None
        )

    @property
    def temperature(self) -> bool:
        return self.get_temperature()

    def get_humidity(self, cached_ms: int = None) -> bool:
        """Return the current XTHL humidity."""
        response = self._ecort2.get(self._humidity_get_link, cached_ms=cached_ms)
        return (
            response[self._humidity_get_entry]
            if (self._humidity_get_entry) in response
            else None
        )

    @property
    def humidity(self) -> bool:
        return self.get_humidity()

    def get_luminosity(self, cached_ms: int = None) -> bool:
        """Return the current XTHL luminosity."""
        response = self._ecort2.get(self._luminosity_get_link, cached_ms=cached_ms)
        return (
            response[self._luminosity_get_entry]
            if (self._luminosity_get_entry) in response
            else None
        )

    @property
    def luminosity(self) -> bool:
        return self.get_luminosity()
