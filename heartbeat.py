import logging
from datetime import datetime
from firebase_admin import db
import time
from getmac import get_mac_address
from decouple import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Heartbeat:
    state = "STOP"
    
    @classmethod
    def update(cls, ETH_MAC):
        now = str(datetime.now())
        ref = db.reference(f"/{ETH_MAC}")
        ref.update({
            "last_heartbeat": now
        })

    @classmethod
    def start(cls, ETH_MAC):
        logger.info("start heartbeat")
        cls.state = "START"
        interval = int(config("HEARTBEAT_INTERVAL", default=600))
        count_down = interval
        while True:
            if cls.state == "START":
                if count_down > 0:
                    count_down -= 1
                    time.sleep(1)
                else:
                    cls.update(ETH_MAC)
                    count_down = interval
            else:
                logger.info("HeartBeat state is not 'START', break loop")
                break

    @classmethod
    def stop(cls):
        cls.state = "STOP"
