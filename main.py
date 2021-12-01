import logging
import os
import socket
from datetime import datetime
import threading

import firebase_admin
from decouple import config
from firebase_admin import db
from getmac import get_mac_address
from pyngrok import conf

from cam_controller import CamController
from heartbeat import Heartbeat
from ngrok_controller import NgrokController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("starting ngrok daemon... "+ETH_MAC+" / "+LOCAL_IP)
    conf.get_default().region = 'au'
    init_data_on_firebase(ETH_MAC)
    ref = db.reference(f"/{ETH_MAC}")
    ref.update({"ip": LOCAL_IP})
    ref.listen(listener)
    Heartbeat_looping = threading.Thread(target=Heartbeat.start(ETH_MAC))
    Heartbeat_looping.start()
    print("heartbeat start")


def listener(event):
    ref = db.reference(f"/{ETH_MAC}")
    if event.path == "/ngrok" and event.data == "ON":
        logger.info("starting ngrok...")
        try:
            NgrokController.start()
            CamController.start()
            ref.update({'ngrok_url': NgrokController.public_urls})
            ref.update({'err': None})
        except:
            ref.update({'err': "something went wrong"})
            NgrokController.stop()
            CamController.stop()
    elif event.path == "/ngrok" and event.data != "ON":
        logger.info("stopping ngrok...")
        NgrokController.stop()
        CamController.stop()
        ref.update({'ngrok_url': None})
        ref.update({'err': None})
    else:
        pass


def init_data_on_firebase(mac):
    ref = db.reference("/")
    ref.update({mac: {
        'name':  config('DEVICE_NAME', default='unnamed'),
        'ngrok': 'OFF',
        'last_reboot': str(datetime.now()),
        'last_heartbeat': str(datetime.now()),
        'ngrok_url': None,
        'expose_ports': NgrokController.expose_ports
    }})


def get_self_ip_address():
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
    os.system(f'ngrok authtoken {config("NGROK_TOKEN", default=None)}')

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
    LOCAL_IP = get_self_ip_address()

    if envisset():
        main()
