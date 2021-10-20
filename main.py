import logging
import os
import socket
from datetime import datetime

import firebase_admin
from decouple import config
from firebase_admin import db
from getmac import get_mac_address
from pyngrok import ngrok


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("starting ngrok daemon... "+ETH_MAC+" / "+LOCAL_IP)
    init_data_on_firebase(ETH_MAC)
    ref = db.reference(f"/{ETH_MAC}")
    ref.update({"ip": LOCAL_IP})
    ref.listen(listener)


def listener(event):
    ref = db.reference(f"/{ETH_MAC}")
    if event.path == "/ngrok" and event.data == "ON":
        logger.info("starting ngrok...")
        NgrokController.start()
        ref.update({'ngrok_url': NgrokController.public_url})
    elif event.path == "/ngrok" and event.data != "ON":
        logger.info("stopping ngrok...")
        NgrokController.stop()
        ref.update({'ngrok_url': None})
    else:
        pass


class NgrokController:
    public_url = None
    auth_token = config('NGROK_TOKEN', default=None)
    ssh_tunnel = None

    @classmethod
    def start(cls):
        cls.ssh_tunnel = ngrok.connect(int(config('EXPOSE_PORT', default=22)), "tcp")
        cls.public_url = cls.ssh_tunnel.public_url
        logger.info(cls.ssh_tunnel)  # NgrokTunnel: "tcp://x.tcp.ngrok.io:xxxxx" -> "localhost:22"

    @classmethod
    def stop(cls):
        if cls.ssh_tunnel is not None:
            public_url = cls.ssh_tunnel.public_url
            cls.ssh_tunnel = ngrok.disconnect(public_url)
            ngrok.kill()
            cls.public_url = None
            logger.info('ngrok stopped')


def init_data_on_firebase(mac):
    ref = db.reference("/")
    ref.update({mac: {
        'name':  config('DEVICE_NAME', default='unnamed'),
        'ngrok': 'OFF',
        'last_reboot': str(datetime.now()),
        'ngrok_url': None,
    }})


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def envisset() -> bool:
    if not config('DATABASE_URL', default=None):
        logger.error("Please setup DATABASE_URL for firebase in .env")
        return False
    elif not config('NGROK_TOKEN', default=None):
        logger.error("Please setup NGROK_TOKEN for ngrok in .env")
        return False

    try:
        base_dir = os.path.dirname(os.path.realpath(__file__))
        firebase_admin.initialize_app(
            firebase_admin.credentials.Certificate(base_dir+'/serviceAccountKey.json'),
            {
                'databaseURL': config('DATABASE_URL', default=None),
            }
        )
    except Exception as e:
        logger.error("firebase admin initialize failed")
        logger.error("please check if firebase 'serviceAccountKey.json' is set in root dir")
        raise e
    return True


if __name__ == '__main__':
    ETH_MAC = get_mac_address()
    LOCAL_IP = get_ip_address()

    if envisset():
        main()