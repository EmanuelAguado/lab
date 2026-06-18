import socket
import threading
import json

class SocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.plugin = None
        self.server_socket = None
        self.server_thread = None
        self.server_running = False

    def handle_client(self, client_socket):
        try:
            while True:
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break
                response = self.handle_request(request)
                client_socket.send(response.encode('utf-8'))
        finally:
            client_socket.close()

    def handle_request(self, request):
        try:
            data = json.loads(request)
            method = data['method']
            params = data['params']
            if hasattr(self.plugin, method):
                func = getattr(self.plugin, method)
                result = func(**params)
                response = json.dumps({'status': 'success', 'data': result})
            else:
                response = json.dumps({'status': 'error', 'message': 'Method not found'})
        except Exception as e:
            response = json.dumps({'status': 'error', 'message': str(e)})
        return response

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1)  # Set timeout to make the socket non-blocking
        self.server_running = True
        print(f"Server listening on {self.host}:{self.port}")
        try:
            while self.server_running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"Accepted connection from {addr}")
                    client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_handler.start()
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"Server stopped: {e}")
        finally:
            self.server_socket.close()

    def start(self):
        if self.server_thread is None:
            self.server_thread = threading.Thread(target=self.start_server)
            self.server_thread.start()

    def stop(self):
        self.server_running = False
        if self.server_socket:
            self.server_socket.close()
        if self.server_thread:
            self.server_thread.join()
            self.server_thread = None

    def set_plugin(self, plugin):
        self.plugin = plugin