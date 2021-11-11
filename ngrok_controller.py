import ast
from pyngrok import ngrok
from decouple import config
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NgrokController:
    public_urls = None
    auth_token = config('NGROK_TOKEN', default=None)
    ssh_tunnels = None
    expose_ports = ast.literal_eval(config('EXPOSE_PORT', default="[22]"))

    @classmethod
    def start(cls):
        cls.ssh_tunnels = [ngrok.connect(p, "tcp") for p in cls.expose_ports]
        cls.public_urls = [t.public_url for t in cls.ssh_tunnels]
        logger.info(cls.ssh_tunnels)  # NgrokTunnel: "tcp://x.tcp.ngrok.io:xxxxx" -> "localhost:22"

    @classmethod
    def stop(cls):
        if cls.ssh_tunnels is not None:
            for t in cls.ssh_tunnels:
                public_url = t.public_url
                ngrok.disconnect(public_url)
            ngrok.kill()
            cls.public_urls = None
            logger.info('ngrok stopped')