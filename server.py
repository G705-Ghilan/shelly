import time
import socket
import pickle
import threading

from cmdl import Cmdl
from typing import Union
from utils import progress, prompet, print

PORT: int = 4444
HEADER: int = 64
FORMAT: str = "utf-8"
HOST: str = "localhost"
CHUNK_SIZE: int = 1024*512
SERVER: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR: tuple = (HOST, PORT)


class Server:
    def __init__(self) -> None:
        self.clients: list = []
        self.server: socket.socket = SERVER
        self.server.bind(ADDR)
        self.cmdl: Cmdl = Cmdl(self)
        self.active_client_index = 0

    @property
    def active_client(self) -> socket:
        return self.clients[self.active_client_index][0]

    @property
    def active_client_data(self) -> tuple:
        return self.clients[self.active_client_index]

    def _listen(self) -> None:
        while True:
            conn, addr = self.server.accept()
            print(f"\nNew {addr}")
            print(self.cmdl.prompt, end="")
            self.clients.append((conn, addr))

    def refresh_cmd(self) -> None:
        self.cmdl.prompt = prompet(
            self.cmdl.client_path, self.active_client_data[-1], str(len(self.clients)))

    def listen(self) -> None:
        self.server.listen()
        thread: threading.Thread = threading.Thread(target=self._listen)
        thread.start()
        with progress(f"Listening on {ADDR} ...") as p:
            while not self.clients:
                time.sleep(0.4)
                p.update(0,description="fjajfj")

        print("# Connected now enjoy with shelly :) ...")
        self.cmdl.do_cd(".")
        self.refresh_cmd()
        self.cmdl.cmdloop()

    def send(self, msg: bytes) -> None:
        length: int = len(msg)
        self.active_client.send(
            f"{length}{' ' * (HEADER - len(str(length)))}".encode(FORMAT))
        self.active_client.send(msg)

    def recv(self, decode: bool = True) -> Union[bytes, str]:
        if (rc := self.active_client.recv(HEADER)):
            length: int = int(rc.decode(FORMAT))
            recved: bytes = self.active_client.recv(length)
        else:
            recved: bytes = rc
        return recved.decode(FORMAT) if decode else recved

    def recv_pickled_data(self) -> dict:
        return pickle.loads(self.recv(decode=False))
