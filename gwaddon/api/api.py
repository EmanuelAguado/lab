import socket
import json

class SocketClient:
    def __init__(self, host="localhost", port=9999):
        self.host = host
        self.port = port
        plugin_info = self.send_request('get_plugin_info', {})
        if plugin_info['status'] == 'success':
            methods = plugin_info['data']['methods']
            variables = plugin_info['data']['variables']
            for method in methods:
                def create_function(method_name):
                    def func(**kwargs):
                        return client.send_request(method_name, kwargs)
                    return func

                globals()[method] = create_function(method)
    
    def send_request(self, method, params):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            request = json.dumps({'method': method, 'params': params})
            s.sendall(request.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            return json.loads(response)






# Ejemplo de uso
if __name__ == '__main__':
    client = SocketClient('localhost', 9999)

    print(client.add_task(id=1, name="Task 1", description="Description for Task 1"))
    print(client.add_task(id=2, name="Task 2", description="Description for Task 2"))
    print(client.modify_task(id=1, description="Updated description for Task 1"))
    print(client.remove_task(id=2))
    print(client.return_task(id=1))
    print(client.return_all_tasks())



