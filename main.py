#! /usr/bin/env python
import socket
from dotenv import load_dotenv
from datetime import datetime
from getmac import get_mac_address
from pyngrok import ngrok
import firebase_admin
from firebase_admin import db
import os


load_dotenv()


def main():
    print("starting ngrok daemon... ", ETH_MAC, LOCAL_IP)
    init_data_on_firebase(ETH_MAC)
    ref = db.reference(f"/{ETH_MAC}")
    ref.update({"ip": LOCAL_IP})
    ref.listen(listener)


def listener(event):
    ref = db.reference(f"/{ETH_MAC}")
    if event.path == "/ngrok" and event.data == "ON":
        print("starting ngrok...")
        NgrokController.start()
        ref.update({'ngrok_url': NgrokController.public_url})
    elif event.path == "/ngrok" and event.data != "ON":
        print("stopping ngrok...")
        NgrokController.stop()
        ref.update({'ngrok_url': None})
    else:
        pass


class NgrokController:
    public_url = None
    auth_token = os.getenv('NGROK_TOKEN')
    ssh_tunnel = None

    @classmethod
    def start(cls):
        cls.ssh_tunnel = ngrok.connect(22, "tcp")
        cls.public_url = cls.ssh_tunnel.public_url
        print(cls.ssh_tunnel)  # NgrokTunnel: "tcp://x.tcp.ngrok.io:xxxxx" -> "localhost:22"

    @classmethod
    def stop(cls):
        if cls.ssh_tunnel is not None:
            public_url = cls.ssh_tunnel.public_url
            cls.ssh_tunnel = ngrok.disconnect(public_url)
            ngrok.kill()
            cls.public_url = None
            print('ngrok stopped')


def mac_is_init(mac):
    ref = db.reference(f"/{mac}")
    resp = ref.get()
    if resp is None:
        return False
    else:
        return True


def init_data_on_firebase(mac):
    ref = db.reference(f"/")
    ref.update({mac: {
        'name': os.getenv('DEVICE_NAME'),
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


def envisset():
    if not os.getenv('DATABASE_URL'):
        print("Please setup DATABASE_URL for firebase in .env")
        return False
    elif not os.getenv('NGROK_TOKEN'):
        print("Please setup NGROK_TOKEN for ngrok in .env")
        return False

    try:
        base_dir = os.path.dirname(os.path.realpath(__file__))
        firebase_admin.initialize_app(
            firebase_admin.credentials.Certificate(base_dir+'/serviceAccountKey.json'),
            {
                'databaseURL': os.getenv('DATABASE_URL'),
            }
        )
    except Exception as e:
        print("firebase admin initialize failed")
        print("please check if firebase 'serviceAccountKey.json' is set in root dir")
        raise e
    return True


if __name__ == '__main__':
    ETH_MAC = get_mac_address()
    LOCAL_IP = get_ip_address()

    if envisset():
        main()