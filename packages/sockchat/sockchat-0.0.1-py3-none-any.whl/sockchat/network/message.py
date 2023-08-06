from dataclasses import dataclass
from enum import IntEnum, auto
from json import dumps, loads


# noinspection PyArgumentList
class MessageType(IntEnum):
    LOGIN = auto()
    TEXT = auto()
    ACK = auto()
    DISCONNECT = auto()


@dataclass
class Message:
    pass


@dataclass
class LoginMessage(Message):
    name: str


# id сообщения указывает порядковый номер сообщения в клиенте. id сообщений разных пользователей могут совпадать
@dataclass
class TextMessage(Message):
    username: str
    text: str
    id: int


@dataclass
class AckMessage(Message):
    """Подтверждение о доставке сообщения с id [id] пользователю [username]"""
    text_by_username: str  # Имя клиента который отправил изначальное сообщение
    acknowledged_by_username: str  # Имя клиента, получившего сообщение
    id: int  # id сообщения в клиенте [text_by_username]


@dataclass
class DisconnectMessage(Message):
    pass


def encode_message(message: Message) -> str:
    if isinstance(message, LoginMessage):
        return dumps({"type": MessageType.LOGIN, "name": message.name})
    elif isinstance(message, TextMessage):
        return dumps({"type": MessageType.TEXT, "username": message.username, "text": message.text, "id": message.id})
    elif isinstance(message, AckMessage):
        return dumps({"type": MessageType.ACK, "text_by_username": message.text_by_username,
                      "acknowledged_by_username": message.acknowledged_by_username, "id": message.id})
    elif isinstance(message, DisconnectMessage):
        return dumps({"type": MessageType.DISCONNECT})


def decode_message(s: str) -> Message:
    dictionary = loads(s)
    if dictionary["type"] == MessageType.LOGIN:
        return LoginMessage(dictionary["name"])
    elif dictionary["type"] == MessageType.TEXT:
        return TextMessage(dictionary["username"], dictionary["text"], dictionary["id"])
    elif dictionary["type"] == MessageType.ACK:
        return AckMessage(dictionary["text_by_username"], dictionary["acknowledged_by_username"], dictionary["id"])
    elif dictionary["type"] == MessageType.DISCONNECT:
        return DisconnectMessage()
