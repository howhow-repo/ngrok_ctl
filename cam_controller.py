import logging
import subprocess
import signal
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CamController:
    process = None

    @staticmethod
    def start():
        if CamController.process is None:
            CamController.process = subprocess.Popen(args=['sudo', 'motion'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            logger.info("cam service started")
        else:
            logger.info(f"cam has started at pid {CamController.process.pid}, do nothing.")

    @staticmethod
    def stop():
        if CamController.process is not None:
            os.system(f"sudo pkill -9 -P {CamController.process.pid}")
            logger.info("cam service stopped")
            CamController.process = None
        else:
            logger.info(f"cam service is already stop, do nothing.")
