import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CamController:
    process = None

    @classmethod
    def start(cls):
        if cls.process is None:
            cls.process = subprocess.Popen(['sudo', 'motion'])
            logger.info("cam service started")
        else:
            logger.info(f"cam has started at pid {cls.process.pid}, do nothing.")

    @classmethod
    def stop(cls):
        if cls.process is not None:
            cls.process.kill()
            logger.info("cam service stopped")
            cls.process = None
        else:
            logger.info(f"cam service is already stop, do nothing.")
