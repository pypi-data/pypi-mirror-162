"""Constances of inels-mqtt."""
from __future__ import annotations
from typing import Final


NAME = "inels-mqtt"

SWITCH = "switch"
SENSOR = "sensor"
LIGHT = "light"

# device types
DEVICE_TYPE_DICT = {
    "02": SWITCH,
    "10": SENSOR,
    "05": LIGHT,
}

PLUG = "plug"
TEMPERATURE = "temperature"
DIMMER = "dimmer"

INELS_DEVICE_TYPE_DICT = {"02": PLUG, "10": TEMPERATURE, "05": DIMMER}

BATTERY = "battery"
TEMP_IN = "temp_in"
TEMP_OUT = "temp_out"
RAMP_UP = "ramp_up"  # náběh
TIME_RAMP_UP = "time_ramp"  # časový náběh
TIME_RAMP_DOWN = "time_ramp_down"  # časový doběh
TEST_COMMUNICATION = "test_communication"

ANALOG_REGULATOR_SET_BYTES = {
    DIMMER: "01",
    RAMP_UP: "02",
    TIME_RAMP_UP: "05",
    TIME_RAMP_DOWN: "06",
    TEST_COMMUNICATION: "07",
}

DEVICE_TYPE_05_HEX_VALUES = {
    "D8\nEF\n": 0,
    "D1\n1F\n": 10,
    "C9\n4F\n": 20,
    "C1\n7F\n": 30,
    "B9\nAF\n": 40,
    "B1\nDF\n": 50,
    "AA\n0F\n": 60,
    "A2\n3F\n": 70,
    "9A\n6F\n": 80,
    "92\n9F\n": 90,
    "8A\nCF\n": 100,
}

DEVICE_TYPE_05_DATA = {DIMMER: [0, 1]}

TEMP_SENSOR_DATA = {BATTERY: [0], TEMP_IN: [2, 1], TEMP_OUT: [4, 3]}

DISCOVERY_TIMEOUT_IN_SEC = 5

FRAGMENT_DOMAIN = "fragment_domain"
FRAGMENT_SERIAL_NUMBER = "fragment_serial_number"
FRAGMENT_STATE = "fragment_state"
FRAGMENT_DEVICE_TYPE = "fragment_device_type"
FRAGMENT_UNIQUE_ID = "fragment_unique_id"

MQTT_BROKER_CLIENT_NAME = "inels-mqtt"
MQTT_DISCOVER_TOPIC = "inels/status/#"

TOPIC_FRAGMENTS = {
    FRAGMENT_DOMAIN: 0,
    FRAGMENT_STATE: 1,
    FRAGMENT_SERIAL_NUMBER: 2,
    FRAGMENT_DEVICE_TYPE: 3,
    FRAGMENT_UNIQUE_ID: 4,
}

DEVICE_CONNCTED = {
    "on\n": True,
    "off\n": False,
}

SWITCH_ON_STATE = "02\n01\n"
SWITCH_OFF_STATE = "02\n00\n"

SWITCH_ON_SET = "01\n00\n00\n"
SWITCH_OFF_SET = "02\n00\n00\n"

SWITCH_SET = {
    True: SWITCH_ON_SET,
    False: SWITCH_OFF_SET,
}

SWITCH_STATE = {
    SWITCH_ON_STATE: True,
    SWITCH_OFF_STATE: False,
}

LIGHT_ON = "Aadfadfadf"
LIGHT_OFF = "adfwerafad"

DEVICE_PLATFORMS = {
    SWITCH: {SWITCH_ON_STATE: True, SWITCH_OFF_STATE: False},
    LIGHT: {LIGHT_ON: True, LIGHT_OFF: False},
}

MQTT_TRANSPORTS = {"tcp", "websockets"}

MQTT_TIMEOUT: Final = "timeout"
MQTT_HOST: Final = "host"
MQTT_USERNAME: Final = "username"
MQTT_PASSWORD: Final = "password"
MQTT_PORT: Final = "port"
MQTT_CLIENT_ID: Final = "client_id"
MQTT_PROTOCOL: Final = "protocol"
MQTT_TRANSPORT: Final = "transport"
PROTO_31 = "3.1"
PROTO_311 = "3.1.1"
PROTO_5 = 5

VERSION = "0.0.1"
