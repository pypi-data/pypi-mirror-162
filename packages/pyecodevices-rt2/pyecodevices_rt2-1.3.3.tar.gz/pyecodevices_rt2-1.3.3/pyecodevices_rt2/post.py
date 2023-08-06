from . import EcoDevicesRT2
from .const import RT2_API


class Post:
    """Class representing the Post or Sub-Post"""

    def __init__(
        self, ecort2: EcoDevicesRT2, id_post: int, id_subpost: int = None
    ) -> None:
        self._ecort2 = ecort2
        self._id_post = id_post
        self._id_subpost = id_subpost
        if id_subpost is not None:
            self._type = "subpost"
        else:
            self._id_subpost = ""
            self._type = "post"

        self._instant_get_link = RT2_API[self._type]["instant"]["get"]["link"]
        self._instant_get_entry = RT2_API[self._type]["instant"]["get"]["entry"] % (
            self._id_post,
            self._id_subpost,
        )
        self._index_get_link = RT2_API[self._type]["index"]["get"]["link"]
        self._index_get_entry = RT2_API[self._type]["index"]["get"]["entry"] % (
            self._id_post,
            self._id_subpost,
        )
        self._index_day_get_link = RT2_API[self._type]["index_day"]["get"]["link"]
        self._index_day_get_entry = RT2_API[self._type]["index_day"]["get"]["entry"] % (
            self._id_post,
            self._id_subpost,
        )
        self._price_get_link = RT2_API[self._type]["price"]["get"]["link"]
        self._price_get_entry = RT2_API[self._type]["price"]["get"]["entry"] % (
            self._id_post,
            self._id_subpost,
        )
        self._price_day_get_link = RT2_API[self._type]["price_day"]["get"]["link"]
        self._price_day_get_entry = RT2_API[self._type]["price_day"]["get"]["entry"] % (
            self._id_post,
            self._id_subpost,
        )

    def get_instant(self, cached_ms: int = None) -> float:
        """Return the instant power of post/subpost."""
        response = self._ecort2.get(self._instant_get_link, cached_ms=cached_ms)
        return (
            response[self._instant_get_entry]
            if (self._instant_get_entry) in response
            else None
        )

    @property
    def instant(self) -> float:
        return self.get_instant()

    def get_index(self, cached_ms: int = None) -> float:
        """Return the index of post/subpost."""
        response = self._ecort2.get(self._index_get_link, cached_ms=cached_ms)
        return (
            response[self._index_get_entry]
            if (self._index_get_entry) in response
            else None
        )

    @property
    def index(self) -> float:
        return self.get_index()

    def get_index_day(self, cached_ms: int = None) -> float:
        """Return the index of the current day of post/subpost."""
        response = self._ecort2.get(self._index_day_get_link, cached_ms=cached_ms)
        return (
            response[self._index_day_get_entry]
            if (self._index_day_get_entry) in response
            else None
        )

    @property
    def index_day(self) -> float:
        return self.get_index_day()

    def get_price(self, cached_ms: int = None) -> float:
        """Return the price of post/subpost."""
        response = self._ecort2.get(self._price_get_link, cached_ms=cached_ms)
        return (
            response[self._price_get_entry]
            if (self._price_get_entry) in response
            else None
        )

    @property
    def price(self) -> float:
        return self.get_price()

    def get_price_day(self, cached_ms: int = None) -> float:
        """Return the price of the current day of post/subpost."""
        response = self._ecort2.get(self._price_day_get_link, cached_ms=cached_ms)
        return (
            response[self._price_day_get_entry]
            if (self._price_day_get_entry) in response
            else None
        )

    @property
    def price_day(self) -> float:
        return self.get_price_day()
