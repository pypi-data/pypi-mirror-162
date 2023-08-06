import subprocess
import docker
from threading import Thread

service_tags = ['store', 'auth', 'mysql', 'mongodb', 'redis']


def get_containers_on_same_network(network_name):
    client = docker.from_env()
    containers = []
    for container in client.containers.list():
        network_config = container.attrs['NetworkSettings']['Networks'].get(
            network_name)
        if network_config:
            containers.append(container)
    return containers


def assign_service_type_tag(containers, prefix: str):
    client = docker.from_env()
    containers_tags = {}
    for container in containers:
        container_name = container.attrs['Name']
        container_name_without_prefix = container_name.replace(
            f"/{prefix}-", '')
        for tag in service_tags:
            if tag in container_name_without_prefix:
                containers_tags[tag] = {
                    'id': container.id,
                    'name': container_name,
                    'state': container.attrs['State']['Running']
                }
    return containers_tags


def restart_containers(container_id):

    restart_thread = Thread(target=threaded_container_restart, args=(container_id, ))
    restart_thread.start()
    return True

def exec_run(container_id, cmd):
    client = docker.from_env()
    container = client.containers.get(container_id)
    codes = container.exec_run(cmd)
    return codes
    
def threaded_container_restart(container_id):
    client = docker.from_env()
    container = client.containers.get(container_id)
    container.restart()
    return True


def compose_up(dir: str, compose_file: str = 'docker-compose.yaml'):
    process = subprocess.run(
        f"docker compose -f {dir}/{compose_file} up -d", shell=True)
    if process.returncode != 0:
        return False
    else:
        return True


def compose_down(dir: str, compose_file: str = 'docker-compose.yaml'):
    process = subprocess.run(
        f"docker compose -f {dir}/{compose_file} down", shell=True)
    if process.returncode != 0:
        return False
    else:
        return True
