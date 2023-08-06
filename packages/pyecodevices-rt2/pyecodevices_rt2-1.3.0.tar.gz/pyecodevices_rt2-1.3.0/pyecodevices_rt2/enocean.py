from . import AbstractSensor
from . import AbstractSwitch
from . import EcoDevicesRT2
from .const import RT2_API


class EnOceanSwitch(AbstractSwitch):
    """Class representing the EnOceanSwitch"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        value_get_link = RT2_API["enocean_switch"]["value"]["get"]["link"]
        value_get_entry = RT2_API["enocean_switch"]["value"]["get"]["entry"]
        value_set_link_on = RT2_API["enocean_switch"]["value"]["set"]["link_on"]
        value_set_link_off = RT2_API["enocean_switch"]["value"]["set"]["link_off"]
        value_set_link_toggle = RT2_API["enocean_switch"]["value"]["set"]["link_toggle"]
        super(EnOceanSwitch, self).__init__(
            ecort2,
            id,
            value_get_link,
            value_get_entry,
            value_set_link_on,
            value_set_link_off,
            value_set_link_toggle,
        )


class EnOceanSensor(AbstractSensor):
    """Class representing the EnOceanSensor"""

    def __init__(self, ecort2: EcoDevicesRT2, id: int) -> None:
        value_get_link = RT2_API["enocean_sensor"]["value"]["get"]["link"]
        value_get_entry = RT2_API["enocean_sensor"]["value"]["get"]["entry"]
        super(EnOceanSensor, self).__init__(ecort2, id, value_get_link, value_get_entry)
