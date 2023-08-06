import logging
import os
from urllib.error import HTTPError
from warnings import catch_warnings

from requests import Response, exceptions, get, post
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

logger = logging.getLogger(__name__)


class MinioContainer(DockerContainer):
    def __init__(self, image="minio/minio:RELEASE.2022-08-08T18-34-09Z"):
        super(MinioContainer, self).__init__(image)

        self.with_exposed_ports(9000).with_env("MINIO_ACCESS_KEY", "testtest").with_env(
            "MINIO_SECRET_KEY", "testtest"
        ).with_command("server /data")

    def accessKey(self):
        return self.env["MINIO_ACCESS_KEY"]

    def secretKey(self):
        return self.env["MINIO_SECRET_KEY"]

    @wait_container_is_ready(exceptions.ConnectionError, exceptions.ReadTimeout)
    def _connect(self):
        url = f"{self.get_url()}/minio/health/live"
        logger.info("Connecting to %s", url)
        res: Response = get(url)
        res.raise_for_status()

    def get_url(self):
        port = self.get_exposed_port(9000)
        host = self.get_container_host_ip()
        return f"http://{host}:{port}"

    def start(self):
        super().start()
        self._connect()
        return self
