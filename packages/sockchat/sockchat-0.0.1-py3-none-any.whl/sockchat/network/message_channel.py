import io
import socket
from threading import Lock
from typing import Optional


class MessageChannel:
    """Канал для передачи целых сообщений по сокету"""

    sock: socket.SocketType
    file: io.TextIOBase

    # В процессе приёма сообщения поток должен иметь эксклюзивный доступ к каналу
    recv_lock: Lock
    # Так же с отправкой сообщения
    send_lock: Lock

    def __init__(self, sock: socket.SocketType):
        self.sock = sock

        # Сокет оборачивается в файл для автоматического кодирования сообщений в utf-8 и обратно,
        # а так же для более точного контроля за количеством считываемых символов
        self.file = sock.makefile(mode="rw", encoding="utf-8")
        assert isinstance(self.file, io.TextIOBase)

        self.recv_lock = Lock()
        self.send_lock = Lock()

        # print("Channel created")

    def send(self, message: str):
        # self.sock.sendall(bytes(str(len(message))))
        # self.sock.sendall(bytes(message))

        # print(f"debug: sending {message}")

        with self.send_lock:
            try:
                # Отправить длину строки
                self.file.write(str(len(message)))
                # Отправить терминатор длины
                self.file.write("$")

                # Отправить строку
                self.file.write(message)
                self.file.flush()
            except ValueError:
                pass

    def receive(self) -> Optional[str]:
        with self.recv_lock:
            # Принять длину строки
            length = 0
            while True:
                char: str
                try:
                    char = self.file.read(1)
                except ConnectionResetError:
                    return None
                except ConnectionAbortedError:
                    return None
                except ValueError:
                    return None

                # print("debug: receiving character", char)
                if len(char) == 0:
                    return None
                if char == "$":
                    break

                # Декодирование длины
                length *= 10
                length += char_to_int(char)

            # Принять строку
            data = ""
            while True:
                # file.read может не вернуть всю строку при первом вызове, поэтому мы вызываем ее в цикле
                data_part = self.file.read(length - len(data))
                if len(data_part) == 0:
                    return None
                data += data_part

                # Цикл заканчивается когда вся строка считана
                if length == len(data):
                    break

            return data

    def close(self):
        self.file.close()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


def char_to_int(c: str) -> int:
    assert len(c) == 1
    return ord(c) - ord('0')
