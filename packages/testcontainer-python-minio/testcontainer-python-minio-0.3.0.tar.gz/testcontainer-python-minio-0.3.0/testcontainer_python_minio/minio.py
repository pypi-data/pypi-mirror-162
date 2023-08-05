from requests import get, post, Response, exceptions
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
import logging
import os

logger = logging.getLogger(__name__)


class MinioContainer(DockerContainer):
    def __init__(self, image="minio/minio:RELEASE.2020-03-09T18-26-53Z"):
        super(MinioContainer, self).__init__(image)

        self.with_exposed_ports(9000).with_env("MINIO_ACCESS_KEY", "testtest").with_env(
            "MINIO_SECRET_KEY", "testtest"
        ).with_command("server /data")

    def accessKey(self):
        return self.env["MINIO_ACCESS_KEY"]

    def secretKey(self):
        return self.env["MINIO_SECRET_KEY"]

    @wait_container_is_ready(exceptions.ConnectionError)
    def _connect(self):
        try:
            logger.info("Connecting to %s", self.get_url())
            res: Response = get(self.get_url())
            if res.status_code >= 500:
                logger.info("Wait call received %s status code", res.status_code)
                raise Exception("Not ready")
        except Exception as e:
            logger.debug("Failed to connect", exc_info=True)
            raise e

    def get_url(self):
        port = self.get_exposed_port(9000)
        host = self.get_container_host_ip()
        return f"http://{host}:{port}"

    def start(self):
        super().start()
        self._connect()
        return self
