from . import AbstractSensor
from . import EcoDevicesRT2
from .const import RT2_API


class SupplierIndex(AbstractSensor):
    """Class representing the SupplierIndex"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        value_get_link = RT2_API["supplierindex"]["index"]["get"]["link"]
        value_get_entry = RT2_API["supplierindex"]["index"]["get"]["entry"]
        super(SupplierIndex, self).__init__(ecort2, id, value_get_link, value_get_entry)

        self._price_get_link = RT2_API["supplierindex"]["price"]["get"]["link"]
        self._price_get_entry = RT2_API["supplierindex"]["price"]["get"]["entry"] % (
            self._id
        )

    def get_price(self, cached_ms: int = None) -> float:
        """Return the price of supplier index."""
        response = self._ecort2.get(self._price_get_link, cached_ms=cached_ms)
        return (
            response[self._price_get_entry]
            if (self._price_get_entry) in response
            else None
        )

    @property
    def price(self) -> float:
        return self.get_price()
