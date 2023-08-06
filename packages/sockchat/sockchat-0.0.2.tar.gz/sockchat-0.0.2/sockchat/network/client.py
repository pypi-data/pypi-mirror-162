import socket
from dataclasses import dataclass
from functools import cache
from queue import Queue, Empty
from threading import Thread
from typing import Optional

from sockchat import common
from sockchat.colors import username_to_color, reset_color, platform_aware_colored_username
from sockchat.network.message import DisconnectMessage, decode_message, encode_message, LoginMessage, TextMessage, AckMessage
from sockchat.network.message_channel import MessageChannel
from sockchat.ui_provider import UiProvider


@dataclass(init=False, eq=False)
class Client:
    username: str
    server_address: str
    ui_provider: UiProvider

    # id следующего отправленного сообщения
    message_counter: int

    # Канал связи с сервером
    chan: Optional[MessageChannel]
    # Очередь сообщений присланных с сервера. Заполняется отдельным потоком
    incoming_message_queue: Queue

    def __init__(self, username: str, served_address: str, ui_provider: UiProvider):
        self.username = username
        self.server_address = served_address
        self.ui_provider = ui_provider

        self.message_counter = 0
        self.chan = None
        self.incoming_message_queue = Queue()

    def incoming_message_reader(self):
        while True:
            message = self.chan.receive()
            if message is None or isinstance(decode_message(message), DisconnectMessage):
                break
            self.incoming_message_queue.put(message)

    def run(self):
        # self.client_print(self)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_address, common.TCP_PORT))

        self.chan = MessageChannel(s)

        # Отправка сообщения о подключении
        self.chan.send(encode_message(LoginMessage(self.username)))

        Thread(target=self.incoming_message_reader).start()

        self.client_print("client created")

        while True:
            # Запрос сообщения от пользователя
            print(f"sockchat {self.message_counter}> ", end="")
            message = self.ui_provider.get()

            if message is None:
                self.chan.send(encode_message(DisconnectMessage()))
                self.chan.close()
                self.client_print("shutting down")
                break

            if message != "":
                # Отправка сообщения пользователя
                self.chan.send(encode_message(TextMessage(self.username, message, self.message_counter)))
                self.message_counter += 1

            # Вывод новых сообщений от сервера
            try:
                while True:
                    incoming_message = self.incoming_message_queue.get_nowait()
                    decoded_message = decode_message(incoming_message)
                    if isinstance(decoded_message, TextMessage):
                        print(f"new message from {platform_aware_colored_username(decoded_message.username)}:", decoded_message.text)

                        # Подтверждение о доставке сообщения
                        self.chan.send(encode_message(
                            AckMessage(decoded_message.username, self.username, decoded_message.id)))
                    elif isinstance(decoded_message, AckMessage):
                        print(f"message №{decoded_message.id} delivered to "
                              f"{platform_aware_colored_username(decoded_message.acknowledged_by_username)}")
                    else:
                        raise Exception()
            except Empty:
                pass

    def client_print(self, *args, **kwargs):
        print(f"client {self.username}:", *args, **kwargs)
