from . import EcoDevicesRT2


class AbstractSensor:
    """Class representing an AbstractSensor"""

    def __init__(
        self, ecort2: EcoDevicesRT2, id: int, get_link: str, get_entry: str
    ) -> None:
        self._ecort2 = ecort2
        self._id = id
        self._get_link = get_link
        self._get_entry = get_entry

    def get_value(self, cached_ms: int = None) -> float:
        """Return the current AbstractSensor status."""
        response = self._ecort2.get(self._get_link, cached_ms=cached_ms)
        return (
            response[self._get_entry % (self._id)]
            if (self._get_entry % (self._id)) in response
            else None
        )

    @property
    def value(self) -> float:
        return self.get_value()
