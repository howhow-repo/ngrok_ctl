import logging
from datetime import datetime
from firebase_admin import db
import time

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
        beat_interval = 60*30
        count_down = beat_interval
        while True:
            if cls.state == "START":
                if count_down > 0:
                    count_down -= 1
                    time.sleep(1)
                else:
                    cls.update(ETH_MAC)
                    count_down = beat_interval
            else:
                logger.info("HeartBeat state is not 'START', break loop")
                break

    @classmethod
    def stop(cls):
        cls.state = "STOP"
