"""Utility classes."""
import logging

from operator import itemgetter
from typing import Any, Dict

from inelsmqtt.mqtt_client import GetMessageType

from .const import (
    ANALOG_REGULATOR_SET_BYTES,
    COVER,
    DEVICE_TYPE_05_DATA,
    DEVICE_TYPE_05_HEX_VALUES,
    DIMMER,
    LIGHT,
    SENSOR,
    SHUTTER_RFJA_12,
    SHUTTER_SET,
    SHUTTER_STATES,
    SWITCH,
    SWITCH_SET,
    SWITCH_STATE,
    TEMPERATURE,
)

ConfigType = Dict[str, str]
_LOGGER = logging.getLogger(__name__)


class DeviceValue(object):
    """Device value interpretation object."""

    def __init__(
        self,
        device_type: str,
        inels_type: str,
        inels_value: str = None,
        ha_value: Any = None,
        last_value: Any = None,
    ) -> None:
        """initializing device info."""
        self.__inels_status_value = inels_value
        self.__inels_set_value: Any = None
        self.__ha_value = ha_value
        self.__device_type = device_type
        self.__inels_type = inels_type
        self.__last_value = last_value

        if self.__ha_value is None:
            self.__find_ha_value()

        if self.__inels_status_value is None:
            self.__find_inels_value()

    def __find_ha_value(self) -> None:
        """Find and crete device value object."""
        if self.__device_type is SWITCH:
            self.__ha_value = SWITCH_STATE[self.__inels_status_value]
            self.__inels_set_value = SWITCH_SET[self.__ha_value]
        elif self.__device_type is SENSOR:
            if self.__inels_type is TEMPERATURE:
                self.__ha_value = self.__inels_status_value
            else:
                self.__ha_value = self.__inels_status_value
        elif self.__device_type is LIGHT:
            if self.__inels_type is DIMMER:
                self.__ha_value = DEVICE_TYPE_05_HEX_VALUES[self.__inels_status_value]

                trimmed_data = self.__trim_inels_status_values(
                    DEVICE_TYPE_05_DATA, DIMMER, " "
                )
                self.__inels_set_value = (
                    f"{ANALOG_REGULATOR_SET_BYTES[DIMMER]} {trimmed_data}"
                )
            else:
                self.__ha_value = self.__inels_status_value
        elif self.__device_type is COVER:
            ha_val = SHUTTER_STATES.get(self.__inels_status_value)

            self.__ha_value = ha_val if ha_val is not None else self.__last_value
            self.__inels_set_value = SHUTTER_SET[self.__ha_value]

    def __trim_inels_status_values(
        self, selector: dict[str, Any], fragment: str, jointer: str
    ) -> str:
        """Trim inels status from broker into the pure string."""
        data = self.__inels_status_value.split("\n")[:-1]

        selected = itemgetter(*selector[fragment])(data)
        return jointer.join(selected)

    def __find_inels_value(self) -> None:
        """Find inels mqtt value for specific device."""
        if self.__device_type is SWITCH:
            self.__inels_status_value = self.__find_keys_by_value(
                SWITCH_STATE, self.__ha_value, self.__last_value
            )
            self.__inels_set_value = SWITCH_SET.get(self.__ha_value)
        elif self.__device_type is LIGHT:
            if self.__inels_type is DIMMER:
                self.__inels_status_value = self.__find_keys_by_value(
                    DEVICE_TYPE_05_HEX_VALUES,
                    round(self.__ha_value, -1),
                    self.__last_value,
                )
                trimmed_data = self.__trim_inels_status_values(
                    DEVICE_TYPE_05_DATA, DIMMER, " "
                )
                self.__inels_set_value = (
                    f"{ANALOG_REGULATOR_SET_BYTES[DIMMER]} {trimmed_data}"
                )
                self.__ha_value = DEVICE_TYPE_05_HEX_VALUES[self.__inels_status_value]
        elif self.__device_type is COVER:
            if self.__inels_type is SHUTTER_RFJA_12:
                self.__inels_status_value = self.__find_keys_by_value(
                    SHUTTER_STATES, self.__ha_value, self.__last_value
                )
                self.__inels_set_value = SHUTTER_SET.get(self.__ha_value)

    def __find_keys_by_value(self, array: dict, value, last_value) -> Any:
        """Return key from dict by value

        Args:
            array (dict): dictionary where should I have to search
            value Any: by this value I'm goning to find key
        Returns:
            Any: value of the dict key
        """
        keys = list(array.keys())
        vals = list(array.values())
        try:
            index = vals.index(value)
            return keys[index]
        except ValueError as err:
            index = vals.index(last_value)
            _LOGGER.error("Value %s is not in list of %s. Stack %s", value, array, err)

        return keys[index]

    @property
    def ha_value(self) -> Any:
        """Converted value from inels mqtt broker into
           the HA format

        Returns:
            Any: object to corespond to HA device
        """
        return self.__ha_value

    @property
    def inels_status_value(self) -> str:
        """Raw inels value from mqtt broker

        Returns:
            str: quated string from mqtt broker
        """
        return self.__inels_status_value

    @property
    def inels_set_value(self) -> str:
        """Raw inels value for mqtt broker

        Returns:
            str: this is string format value for mqtt broker
        """
        return self.__inels_set_value


def get_value(status: GetMessageType, platform: str) -> Any:
    """Get value from pyload message."""
    if platform == SWITCH:
        return SWITCH_STATE[status]

    return None


def get_state_topic(cfg: ConfigType) -> str:
    """Get state topic."""
    return cfg["DDD"]


def get_set_topic(cfg: ConfigType) -> str:
    """Get set topic."""
    return cfg["OOO"]


def get_name(cfg: ConfigType) -> str:
    """Get name of the entity."""
    return cfg["Name"]
