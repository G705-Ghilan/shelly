from server import Server
from utils import console

if __name__ == "__main__":
    try:
        server: Server = Server()
        server.listen()
    except Exception as e:
        console.print_exception(show_locals=True)