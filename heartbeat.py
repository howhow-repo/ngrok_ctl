import logging
from datetime import datetime
from firebase_admin import db
import time
from decouple import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Heartbeat:
    state = "STOP"
    
    @staticmethod
    def update(ETH_MAC):
        now = str(datetime.now())
        ref = db.reference(f"/{ETH_MAC}")
        ref.update({
            "last_heartbeat": now
        })

    @staticmethod
    def start(ETH_MAC):
        logger.info("start heartbeat")
        Heartbeat.state = "START"
        interval = int(config("HEARTBEAT_INTERVAL", default=600))
        count_down = interval
        while True:
            if Heartbeat.state == "START":
                if count_down > 0:
                    count_down -= 1
                    time.sleep(1)
                else:
                    Heartbeat.update(ETH_MAC)
                    count_down = interval
            else:
                logger.info("HeartBeat state is not 'START', break loop")
                break

    @staticmethod
    def stop():
        Heartbeat.state = "STOP"
