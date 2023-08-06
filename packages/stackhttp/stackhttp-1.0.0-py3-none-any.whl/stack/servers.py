import pyding
import ssl
import socket
import threading

from .request import Request
from .response import Response

class Server:
    """
        Server
        ------
        A simple server.
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.running = False

    def stop(self):
        self.socket.close()
        self.running = False

    def setup_socket(self):
        # Setup socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_socket(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def spin_up(self):
        self.setup_socket()
        self.start_socket()
        self.running = True
        # Pass to the main loop
        self.run()

    def handle_connection(self, connection, address):
        connection.close()

    def run(self):
        while self.running:
            try:
                handler = threading.Thread(target=self.handle_connection, args=self.socket.accept(), daemon=True)
                handler.start()
            except KeyboardInterrupt:
                self.running = False
                break
            except:
                pass
        self.socket.close()

class SSLServer(Server):
    """
    SSLServer
    ----------
    A Simple SSL socket server.
    """
    def __init__(self, host: str, port: int, private_key: str = "", chain: str = ""):
        super().__init__(host, port)
        self.private_key = private_key
        self.chain = chain
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(chain, private_key)

    def start_socket(self):
        super().start_socket()
        self.socket = self.context.wrap_socket(self.socket, server_side=True)


class HTTP(Server):
    def handle_connection(self, connection: socket.socket, address):
        # Init the request
        request = Request()
        response = Response()
        # Get the data from the client and only stop if there is no more data or request is done.
        while not request.complete:
            # Recieve data
            new_data = connection.recv(1)
            # Break if no data is recieved
            if not new_data:
                break
            # Append new data
            request.append_raw_data(new_data)
        print(request.raw_data)
        if "http_request" not in pyding.event_space.global_event_space.events or not pyding.methods.global_event_space.get_handlers("http_request"):
            response.send_file('assets/hello_world.html')
        for data in response.http():
            connection.send(data)
        connection.close()


class HTTPS(SSLServer, HTTP):

    def handle_connection(self, connection, address):
        return super(HTTP).handle_connection(connection, address)