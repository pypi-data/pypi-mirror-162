from . import EcoDevicesRT2
from .const import RESPONSE_ENTRY
from .const import RESPONSE_SUCCESS_VALUE
from .const import RT2_API


class Counter:
    """Class representing the Counter"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        self._ecort2 = ecort2
        self._id = id
        self._value_get_link = RT2_API["counter"]["value"]["get"]["link"]
        self._value_get_entry = RT2_API["counter"]["value"]["get"]["entry"] % (self._id)
        self._value_set_link = RT2_API["counter"]["value"]["set"]["link"]
        self._price_get_link = RT2_API["counter"]["price"]["get"]["link"]
        self._price_get_entry = RT2_API["counter"]["price"]["get"]["entry"] % (self._id)

    def get_value(self, cached_ms: int = None) -> int:
        """Return the current Counter value."""
        response = self._ecort2.get(self._value_get_link, cached_ms=cached_ms)
        return (
            response[self._value_get_entry]
            if (self._value_get_entry) in response
            else None
        )

    @property
    def value(self) -> int:
        return self.get_value()

    @value.setter
    def value(self, value: int) -> bool:
        """Modify the current Counter value."""
        response = self._ecort2.get(self._value_set_link % (self._id, str(value)))
        return response[RESPONSE_ENTRY] == RESPONSE_SUCCESS_VALUE

    def add(self, value: int) -> bool:
        """Add a value to the current Counter value."""
        response = self._ecort2.get(self._value_set_link % (self._id, "+%d" % value))
        return response[RESPONSE_ENTRY] == RESPONSE_SUCCESS_VALUE

    def substrat(self, value: int) -> bool:
        """Substract a value to the current Counter value."""
        response = self._ecort2.get(self._value_set_link % (self._id, "-%d" % value))
        return response[RESPONSE_ENTRY] == RESPONSE_SUCCESS_VALUE

    def get_price(self, cached_ms: int = None) -> float:
        """Return the price of counter."""
        response = self._ecort2.get(self._price_get_link, cached_ms=cached_ms)
        return (
            response[self._price_get_entry]
            if (self._price_get_entry) in response
            else None
        )

    @property
    def price(self, cached_ms: int = None) -> float:
        return self.get_price()
