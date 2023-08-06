from requests import get

def is_port_open(port: int = 80) -> bool:
    """
    Checks if a port is open.
    """
    import socket

    host = [
        "0.0.0.0",
        "localhost",
        "::",
        "::1",
        "127.0.0.1"
    ]
    are_ports_open = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for host_name in host:
        try:
            result = s.connect_ex((host_name, port)) == 0
            are_ports_open.append(result)
        except Exception as _:
            pass
    s.close()
    if True in are_ports_open:
        return False
    else:
        return True


def generate_random_port() -> int:
    """
    Generates a random port.
    """
    import random

    random_port = random.randint(1024, 8000)

    return random_port


def find_open_port(previous_service_port: int = False) -> int:
    """
    Finds an open port.
    """
    if previous_service_port:
        port = previous_service_port + 1
        return port if is_port_open(port) else find_open_port(port)
    else:
        port = generate_random_port()
        while not is_port_open(port):
            port = generate_random_port()
        return port


def get_machine_public_ip() -> str:
    """
    Gets the public id of the server.
    """
    try:
        ip = get('https://server.sampurna-bazaar.com/api/public/ip', timeout=.500).content.decode('utf8')
        return ip
    except Exception as e:
        print(str(e))
        print("Not able to get the public IP of the server.")
        exit()