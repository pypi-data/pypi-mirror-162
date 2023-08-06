from . import AbstractSwitch
from . import EcoDevicesRT2
from .const import RT2_API


class Relay(AbstractSwitch):
    """Class representing the Relay"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        value_get_link = RT2_API["relay"]["value"]["get"]["link"]
        value_get_entry = RT2_API["relay"]["value"]["get"]["entry"]
        value_set_link_on = RT2_API["relay"]["value"]["set"]["link_on"]
        value_set_link_off = RT2_API["relay"]["value"]["set"]["link_off"]
        value_set_link_toggle = RT2_API["relay"]["value"]["set"]["link_toggle"]
        super(Relay, self).__init__(
            ecort2,
            id,
            value_get_link,
            value_get_entry,
            value_set_link_on,
            value_set_link_off,
            value_set_link_toggle,
        )
