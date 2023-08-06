import json
import json.encoder
import logging
import socket
import typing as t
import urllib.parse
from datetime import datetime
from enum import Enum

from paho.mqtt.client import Client as _Client
from paho.mqtt.client import MQTTMessage

from meili_sdk.exceptions import MqttException, UnauthorizedMqttException
from meili_sdk.mqtt.models.state import VDA5050StateMessage
from meili_sdk.site import get_host

logger = logging.getLogger("meili_sdk")

__all__ = ("MeiliMqttClient",)


class MqttConnectionStatus(Enum):
    UNKNOWN = 0
    CONNECTING = 1
    FAILED = 2
    CONNECTED = 3


class MeiliMqttClient:
    """
    Base Meili MQTT Client
    """

    def __init__(
        self,
        client_id: str,
        token: str,
        host: t.Optional[str] = None,
        port=1883,
        open_handler=None,
        disconnect_handler=None,
        message_handler=None,
        subscribe_handler=None,
    ):
        host = host or get_host()
        url = urllib.parse.urlparse(host)

        self.url = url.hostname or url.path
        self.port = port
        self.client_id = client_id

        self.client = _Client(client_id=client_id)
        self.client.username_pw_set(username=client_id, password=token)
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_message = self.__on_message
        self.client.on_subscribe = self.__on_subscribe

        self.__open_handler = open_handler
        self.__disconnect_handler = disconnect_handler
        self.__message_handler = message_handler
        self.__subscribe_handler = subscribe_handler
        self.__topics = {}

        self.connection_state = MqttConnectionStatus.UNKNOWN

    def run(self, block=False):
        try:
            self.connection_state = MqttConnectionStatus.CONNECTING
            self.client.connect(
                self.url, port=self.port, keepalive=True, bind_address=""
            )
        except socket.gaierror as e:
            self.connection_state = MqttConnectionStatus.FAILED
            raise MqttException(
                f"Cannot connect to {self.url}:{self.port}. Maybe it's incorrect URI?"
            ) from e
        if block:
            self.client.loop_forever(timeout=1.0)
        else:
            self.client.loop_start()

    def subscribe(self, *topics):
        self.__check_connection("Cannot subscribe on a closed connection")

        for topic_data in topics:
            if topic_data in self.__topics.values():
                raise ValueError(f"Topic already subscribed to")
            if isinstance(topic_data, (list, tuple, set)) and len(topic_data) == 2:
                topic, qos = topic_data
                if qos < 0 or qos > 3:
                    raise ValueError("qos needs to be between 0 and 3")
            elif isinstance(topic_data, str):
                topic, qos = topic_data, 0
            else:
                raise TypeError("Invalid type of topic provided")
            status, mid = self.client.subscribe(topic, qos=qos)
            self.__topics[mid] = topic

    def disconnect(self):
        self.__check_connection()
        self.client.disconnect()

    def publish(self, topic: str, message: any, qos=0):
        self.__check_connection("Cannot send. Connection is closed")

        if isinstance(message, VDA5050StateMessage):
            message = json.dumps(dict(message), default=str)
        elif not isinstance(message, str):
            try:
                message = json.dumps(message)
            except (TypeError, ValueError):
                message = str(message)

        self.client.publish(topic=topic, payload=message, qos=qos)

    def wait_for_connection(self, timeout=10):
        """
        Block execution until connection is established

        If connection is still closed after timeout provided, it will raise TimeoutError

        If connection was not opened it will raise a ConnectionError
        """
        if self.connection_state in [
            MqttConnectionStatus.UNKNOWN,
            MqttConnectionStatus.FAILED,
        ]:
            raise ConnectionError("Connection is not currently connecting")
        start_time = datetime.now()

        while (
            self.connection_state == MqttConnectionStatus.CONNECTING
            and (datetime.now() - start_time).seconds < timeout
        ):
            continue

        if self.connection_state != MqttConnectionStatus.CONNECTED:
            raise TimeoutError("Timed out")

    def __check_connection(self, custom_message=None):
        if not self.client.is_connected():
            raise ConnectionError(custom_message or "Connection is closed")

    def __on_connect(self, client: _Client, _: t.Optional[dict], flags: dict, rc: int):
        if rc != 0:
            self.connection_state = MqttConnectionStatus.FAILED
            raise UnauthorizedMqttException(
                "Bad credentials provided, cannot authenticate"
            )
        self.connection_state = MqttConnectionStatus.CONNECTED
        self.on_connect(client, flags, rc)

    def __on_subscribe(
        self, client: _Client, _: t.Optional[dict], mid: int, granted_qos: t.Tuple[int]
    ):
        if granted_qos[0] > 3:
            raise UnauthorizedMqttException(
                f"Subscription unauthorized to topic {self.__topics[mid]}"
            )
        self.on_subscribe(client, mid, granted_qos)

    def on_subscribe(self, client: _Client, mid, granted_qos):
        if callable(self.__subscribe_handler):
            self.__subscribe_handler(client, mid, granted_qos)

    def on_connect(self, client: _Client, flags: dict, rc: int):
        if callable(self.__open_handler):
            self.__open_handler(client, flags, rc)

    def __on_disconnect(self, client: _Client, _, rc):
        self.on_disconnect(client, rc)

    def on_disconnect(self, client: _Client, rc):
        if callable(self.__disconnect_handler):
            self.__disconnect_handler(client, rc)

    def __on_message(self, client: _Client, _: t.Optional[dict], message: MQTTMessage):
        try:
            received_data = json.loads(message.payload)
        except json.JSONDecodeError:
            logger.warning(f"Cannot decode JSON from received data: {message.payload}")
            received_data = None
        self.on_message(
            client, message.topic, raw_data=message.payload, data=received_data
        )

    def on_message(
        self,
        client: _Client,
        topic: str,
        raw_data: bytes,
        data: t.Optional[dict] = None,
    ):
        """
        Handle message. If message_handler was provided when initializing the object
        it will call it with parsed and raw data
        """
        if callable(self.__message_handler):
            self.__message_handler(client, topic, raw_data, data)
