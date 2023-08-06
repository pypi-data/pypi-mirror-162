"""Unit tests for Device class
    handling device operations
"""
from operator import itemgetter

from unittest.mock import Mock, patch, PropertyMock
from unittest import TestCase
from inelsmqtt import InelsMqtt
from inelsmqtt.util import DeviceValue
from inelsmqtt.devices import Device, DeviceInfo
from inelsmqtt.const import (
    BATTERY,
    COVER,
    SHUTTER_RFJA_12,
    STATE_CLOSED,
    STATE_OPEN,
    STOP,
    TEMP_IN,
    TEMP_OUT,
    DEVICE_TYPE_DICT,
    FRAGMENT_DEVICE_TYPE,
    FRAGMENT_DOMAIN,
    FRAGMENT_SERIAL_NUMBER,
    FRAGMENT_UNIQUE_ID,
    SWITCH_OFF_SET,
    SWITCH_ON_SET,
    SWITCH_ON_STATE,
    SWITCH_OFF_STATE,
    TEMP_SENSOR_DATA,
    TOPIC_FRAGMENTS,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_PROTOCOL,
    PROTO_5,
)

from tests.const import (
    TEST_COVER_RFJA_12_INELS_STATE_CLOSED,
    TEST_COVER_RFJA_12_INELS_STATE_OPEN,
    TEST_COVER_RFJA_12_SET_CLOSE,
    TEST_COVER_RFJA_12_SET_OPEN,
    TEST_COVER_RFJA_12_SET_STOP,
    TEST_COVER_RFJA_12_TOPIC_CONNECTED,
    TEST_COVER_RFJA_12_TOPIC_STATE,
    TEST_LIGH_STATE_HA_VALUE,
    TEST_LIGH_STATE_INELS_VALUE,
    TEST_LIGHT_DIMMABLE_TOPIC_STATE,
    TEST_LIGHT_SET_INELS_VALUE,
    TEST_SENSOR_TOPIC_STATE,
    TEST_AVAILABILITY_OFF,
    TEST_AVAILABILITY_ON,
    TEST_TEMPERATURE_DATA,
    TEST_SWITICH_TOPIC_CONNECTED,
    TEST_SWITCH_TOPIC_STATE,
    TEST_INELS_MQTT_NAMESPACE,
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_HOST,
    TEST_PORT,
    TEST_USER_NAME,
    TEST_PASSWORD,
)


class DeviceTest(TestCase):
    """Device class tests

    Args:
        TestCase (_type_): Base class of unit testing
    """

    def setUp(self) -> None:
        """Setup all patches and instances for device testing"""
        self.patches = [
            patch(f"{TEST_INELS_MQTT_NAMESPACE}.mqtt.Client", return_value=Mock()),
            patch(
                f"{TEST_INELS_MQTT_NAMESPACE}.mqtt.Client.username_pw_set",
                return_value=Mock(),
            ),
            patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.subscribe", return_value=Mock()),
            patch(f"{TEST_INELS_MQTT_NAMESPACE}._LOGGER", return_value=Mock()),
        ]

        for item in self.patches:
            item.start()

        config = {
            MQTT_HOST: TEST_HOST,
            MQTT_PORT: TEST_PORT,
            MQTT_USERNAME: TEST_USER_NAME,
            MQTT_PASSWORD: TEST_PASSWORD,
            MQTT_PROTOCOL: PROTO_5,
        }

        self.device = Device(InelsMqtt(config), TEST_SWITCH_TOPIC_STATE, "Device")
        self.sensor = Device(InelsMqtt(config), TEST_SENSOR_TOPIC_STATE, "Sensor")
        self.light = Device(InelsMqtt(config), TEST_LIGHT_DIMMABLE_TOPIC_STATE, "Light")
        self.shutter = Device(
            InelsMqtt(config), TEST_COVER_RFJA_12_TOPIC_STATE, "Shutter"
        )

    def tearDown(self) -> None:
        """Destroy all instances and stop patches"""
        self.device = None
        self.sensor = None
        self.light = None
        self.shutter = None

    def test_initialize_device(self) -> None:
        """Test initialization of device object"""
        title = "Device 1"

        # device without title
        dev_no_title = Device(Mock(), TEST_SWITCH_TOPIC_STATE)
        # device with title
        dev_with_title = Device(Mock(), TEST_SWITCH_TOPIC_STATE, title)

        self.assertIsNotNone(dev_no_title)
        self.assertIsNotNone(dev_with_title)

        self.assertIsInstance(dev_no_title, Device)
        self.assertIsInstance(dev_with_title, Device)

        self.assertEqual(dev_no_title.title, dev_no_title.unique_id)
        self.assertEqual(dev_with_title.title, title)

        fragments = TEST_SWITCH_TOPIC_STATE.split("/")

        set_topic = f"{fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]}/set/{fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]}"  # noqa: 501

        self.assertEqual(
            dev_no_title.unique_id, fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]
        )
        self.assertEqual(
            dev_no_title.device_type,
            DEVICE_TYPE_DICT[fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]],
        )
        self.assertEqual(
            dev_no_title.parent_id, fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]
        )

        self.assertEqual(dev_no_title.set_topic, set_topic)
        self.assertEqual(dev_with_title.set_topic, set_topic)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    @patch("inelsmqtt.InelsMqtt.messages", new_callable=PropertyMock)
    def test_set_payload(self, mock_messages, mock_publish) -> None:
        """Test set payload of the device."""
        self.assertTrue(self.device.set_ha_value(True))

        # SWITCH_ON needs to be encoded becasue broker returns value as a byte
        mock_messages.return_value = {TEST_SWITCH_TOPIC_STATE: SWITCH_ON_STATE.encode()}
        mock_publish.return_value = True

        rt_val = self.device.get_value()
        self.assertTrue(rt_val.ha_value)
        self.assertEqual(rt_val.inels_status_value, SWITCH_ON_STATE)
        self.assertEqual(rt_val.inels_set_value, SWITCH_ON_SET)

        self.assertTrue(self.device.set_ha_value(False))

        mock_messages.return_value = {
            TEST_SWITCH_TOPIC_STATE: SWITCH_OFF_STATE.encode()
        }
        mock_publish.return_value = False

        rt_val = self.device.get_value()
        self.assertFalse(rt_val.ha_value)
        self.assertEqual(rt_val.inels_status_value, SWITCH_OFF_STATE)
        self.assertEqual(rt_val.inels_set_value, SWITCH_OFF_SET)

    def test_info_serialized(self) -> None:
        """Test of the serialized info."""
        self.assertIsInstance(self.device.info_serialized(), str)

    def test_info(self) -> None:
        """Test of the info."""
        info = self.device.info()
        fragments = TEST_SWITCH_TOPIC_STATE.split("/")

        self.assertIsInstance(info, DeviceInfo)
        self.assertEqual(info.manufacturer, fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]])

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages", new_callable=PropertyMock)
    def test_is_available(self, mock_messages) -> None:
        """Test of the device availability."""

        mock_messages.return_value = {
            TEST_SWITICH_TOPIC_CONNECTED: TEST_AVAILABILITY_ON
        }
        is_avilable = self.device.is_available

        self.assertTrue(is_avilable)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages", new_callable=PropertyMock)
    def test_is_not_available(self, mock_messages) -> None:
        """Test of the dvice availability wit result false."""

        mock_messages.return_value = {
            TEST_SWITICH_TOPIC_CONNECTED: TEST_AVAILABILITY_OFF
        }
        is_avilable = self.device.is_available

        self.assertFalse(is_avilable)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages", new_callable=PropertyMock)
    def test_temperature_parsing(self, mock_message) -> None:
        """Test parsing teperature data to relevant format."""
        mock_message.return_value = {TEST_SENSOR_TOPIC_STATE: TEST_TEMPERATURE_DATA}

        temp_in_decimal_result = 27.4
        temp_out_decimal_result = 26.7
        batter_decimal_result = 100

        # split by new line and remove last element because is empty
        data = self.sensor.state.split("\n")[:-1]

        self.assertEqual(len(data), 5)

        battery = itemgetter(*TEMP_SENSOR_DATA[BATTERY])(data)
        temp_in = itemgetter(*TEMP_SENSOR_DATA[TEMP_IN])(data)
        temp_out = itemgetter(*TEMP_SENSOR_DATA[TEMP_OUT])(data)

        self.assertEqual(battery, data[0])
        self.assertEqual("".join(temp_in), f"{data[2]}{data[1]}")
        self.assertEqual("".join(temp_out), f"{data[4]}{data[3]}")

        temp_in_joined = "".join(temp_in)
        temp_out_joined = "".join(temp_out)

        temp_in_hex = f"0x{temp_in_joined}"
        temp_out_hex = f"0x{temp_out_joined}"
        battery_hex = f"0x{battery}"

        temp_in_dec = int(temp_in_hex, 16) / 100
        temp_out_dec = int(temp_out_hex, 16) / 100
        battery_dec = 100 if int(battery_hex, 16) == 0 else 0

        self.assertEqual(temp_in_dec, temp_in_decimal_result)
        self.assertEqual(temp_out_dec, temp_out_decimal_result)
        self.assertEqual(battery_dec, batter_decimal_result)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages", new_callable=PropertyMock)
    def test_device_dimmable_light_test_values(self, mock_message) -> None:
        """Test if the light is on."""
        mock_message.return_value = {
            TEST_LIGHT_DIMMABLE_TOPIC_STATE: TEST_LIGH_STATE_INELS_VALUE
        }

        values = self.light.get_value()

        self.assertEqual(self.light.state, TEST_LIGH_STATE_HA_VALUE)
        self.assertEqual(values.ha_value, TEST_LIGH_STATE_HA_VALUE)
        self.assertEqual(
            values.inels_status_value, TEST_LIGH_STATE_INELS_VALUE.decode()
        )
        self.assertEqual(values.inels_set_value, TEST_LIGHT_SET_INELS_VALUE)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages", new_callable=PropertyMock)
    def test_device_set_not_support_dimmable_light_value(
        self, mock_message, mock_publish
    ) -> None:
        """Test result ha and inels value when ha value is not supported in inels."""
        mock_message.return_value = {
            TEST_LIGHT_DIMMABLE_TOPIC_STATE: TEST_LIGH_STATE_INELS_VALUE
        }
        mock_publish.return_value = True

        self.light.set_ha_value(24)

        self.assertEqual(self.light.state, TEST_LIGH_STATE_HA_VALUE)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages", new_callable=PropertyMock)
    def test_device_support_cover_initialized(self, mock_message) -> None:
        """Test covers all props. initialization."""
        mock_message.return_value = {
            TEST_COVER_RFJA_12_TOPIC_STATE: TEST_COVER_RFJA_12_INELS_STATE_OPEN,
            TEST_COVER_RFJA_12_TOPIC_CONNECTED: TEST_AVAILABILITY_ON,
        }

        self.assertTrue(self.shutter.is_available)
        self.assertEqual(self.shutter.device_type, COVER)
        self.assertEqual(self.shutter.inels_type, SHUTTER_RFJA_12)
        self.assertEqual(self.shutter.state, STATE_OPEN)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages", new_callable=PropertyMock)
    def test_device_support_cover_open_stop_and_close(
        self, mock_message, mock_publish
    ) -> None:
        """Test open the shutter."""
        mock_message.return_value = {
            TEST_COVER_RFJA_12_TOPIC_STATE: TEST_COVER_RFJA_12_INELS_STATE_CLOSED,
        }
        mock_publish.return_value = True

        self.assertNotEqual(self.shutter.state, STATE_OPEN)
        self.assertEqual(self.shutter.state, STATE_CLOSED)

        values: DeviceValue = self.shutter.get_value()

        self.assertIsInstance(values, DeviceValue)
        self.assertEqual(
            values.inels_status_value, TEST_COVER_RFJA_12_INELS_STATE_CLOSED.decode()
        )
        self.assertEqual(values.inels_set_value, TEST_COVER_RFJA_12_SET_CLOSE)

        self.shutter.set_ha_value(STATE_OPEN)

        mock_message.return_value = {
            TEST_COVER_RFJA_12_TOPIC_STATE: TEST_COVER_RFJA_12_INELS_STATE_OPEN,
        }

        values: DeviceInfo = self.shutter.get_value()

        self.assertIsInstance(values, DeviceValue)
        self.assertEqual(
            values.inels_status_value, TEST_COVER_RFJA_12_INELS_STATE_OPEN.decode()
        )
        self.assertEqual(values.inels_set_value, TEST_COVER_RFJA_12_SET_OPEN)
        self.assertEqual(self.shutter.state, STATE_OPEN)
        self.assertNotEqual(self.shutter.state, STATE_CLOSED)

        self.shutter.set_ha_value(STOP)
        self.assertEqual(
            self.shutter.values.inels_set_value, TEST_COVER_RFJA_12_SET_STOP
        )
        self.assertEqual(
            self.shutter.values.inels_status_value,
            TEST_COVER_RFJA_12_INELS_STATE_OPEN.decode(),
        )
        self.assertEqual(self.shutter.state, STOP)
