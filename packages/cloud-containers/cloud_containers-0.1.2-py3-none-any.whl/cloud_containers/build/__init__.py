import docker

DOCKER_UNIX_URL='unix://var/run/docker.sock'



class Container:
    def __init__(self, base_url=DOCKER_UNIX_URL) -> None:
        self.client = docker.DockerClient(base_url=base_url)

    def build_container(self, tag, dockerfile):
        return 