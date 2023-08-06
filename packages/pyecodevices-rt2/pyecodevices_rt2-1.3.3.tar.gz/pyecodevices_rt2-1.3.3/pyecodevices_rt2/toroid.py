from . import EcoDevicesRT2
from .const import RT2_API


class Toroid:
    """Class representing the Toroid"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        self._ecort2 = ecort2
        self._id = id

        self._index_get_link = RT2_API["toroid"]["index"]["get"]["link"]
        self._index_get_entry = RT2_API["toroid"]["index"]["get"]["entry"] % (self._id)
        self._price_get_link = RT2_API["toroid"]["price"]["get"]["link"]
        self._price_get_entry = RT2_API["toroid"]["price"]["get"]["entry"] % (self._id)

    def get_value(self, cached_ms: int = None) -> float:
        """Return the index of toroid."""
        response = self._ecort2.get(self._index_get_link, cached_ms=cached_ms)
        return (
            response[self._index_get_entry]
            if (self._index_get_entry) in response
            else None
        )

    @property
    def value(self) -> float:
        return self.get_value()

    def get_price(self, cached_ms: int = None) -> float:
        """Return the price of toroid."""
        response = self._ecort2.get(self._price_get_link, cached_ms=cached_ms)
        return (
            response[self._price_get_entry]
            if (self._price_get_entry) in response
            else None
        )

    @property
    def price(self) -> float:
        return self.get_price()
