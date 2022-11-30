
""" Internal message structure """

import json
from typing import Protocol
from enum import Enum


class MessageEnum(Enum):
    ...


class DeviceMessageEnum(MessageEnum):
    DEVICE_ONLINE = 'DEVICE_ONLINE'
    DEVICE_OFFLINE = 'DEVICE_OFFLINE'
    DEVICE_READOUT = 'DEVICE_READOUT'
    DEVICE_OUT_OF_RANGE = 'DEVICE_OUT_OF_RANGE'


class RepositoryMessageEnum(MessageEnum):
    REPOSITORY_ONLINE = 'REPOSITORY_ONLINE'


class Message(Protocol):
    msg_type: str
    msg_content: str


class DeviceMessage:
    """
    IoT device messages providing the device's readout
    """
    def __init__(self, message_type: str, message: str):
        self.msg_type = message_type
        self.msg_content = message

    @property
    def message_type(self):
        return self.__dict__.get('msg_type')

    @property
    def message(self):
        return self.__dict__.get('msg_content')

    def __str__(self):
        return str(self.__dict__)


class RepositoryMessage:
    """
    Repository messages
    """
    def __init__(self, message_type: str, message: str):
        self.msg_type = message_type
        self.msg_content = message

    @property
    def message_type(self):
        return self.__dict__.get('msg_type')

    @property
    def message(self):
        return self.__dict__.get('msg_content')

    def __str__(self):
        return str(self.__dict__)
