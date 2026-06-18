import socket
import json

from plugin.components import *


class GPlugin:
    host = "localhost"
    port = 9999

    def __init__(self) -> None:
        plugin_info = self.send_request("get_plugin_info", {})
        if plugin_info["status"] == "success":
            methods = plugin_info["data"]["methods"]
            variables = plugin_info["data"]["variables"]
            for method in methods:
                globals()[method] = self.create_function(method)

    def send_request(self, method, params):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            request = json.dumps({"method": method, "params": params})
            s.sendall(request.encode("utf-8"))
            response = s.recv(1024).decode("utf-8")
            return json.loads(response)

    def create_function(self, method_name):
        def func(**kwargs):
            return self.send_request(method_name, kwargs)

        return func


# Ejemplo de uso
if __name__ == "__main__":
    print(add_task(id=1, name="Task 1", description="Description for Task 1"))
    print(add_task(id=2, name="Task 2", description="Description for Task 2"))
    print(modify_task(id=1, description="Updated description for Task 1"))
    print(remove_task(id=2))
    print(return_task(id=1))
    print(return_all_tasks())
