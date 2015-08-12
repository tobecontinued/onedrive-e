"""
Monitor thread for network connectivity. It internally holds a queue for
threads blocked because of network failure.
"""

import queue
import time
import threading

import requests

from . import logger_factory


class NetworkMonitor(threading.Thread):
    THREAD_NAME = "netmon"
    logger = logger_factory.get_logger(__name__)

    def __init__(self, test_uri='https://onedrive.com', retry_delay_sec=30, proxies=None):
        """
        :param str test_uri: The url to use in testing internet connectivity.
        :param int retry_delay_sec: The amount of seconds to wait before retry.
        :param dict[str, str] proxies: A dict of protocol-url pairs.
        """
        super().__init__()
        self.name = NetworkMonitor.THREAD_NAME
        self.daemon = True
        self.test_uri = test_uri
        self.retry_delay = retry_delay_sec
        self.proxies = proxies
        self.queue = queue.Queue()
        self.conditions = {}
        self.logger.info("Initialized.")

    def suspend_caller(self):
        """Put the calling thread into suspension queue."""
        me = threading.current_thread()
        cond = self.conditions[me.ident] = threading.Condition()
        self.queue.put(me)
        self.logger.info("Suspended due to network failure.")
        cond.acquire()
        # Put the caller thread to sleep
        cond.wait()
        # Thread is waken up by manager
        cond.release()
        del self.conditions[me.ident]
        self.logger.info("Resumed.")

    def is_connected(self):
        """
        Test if internet connection is OK by connecting to the test URI provided.
        If proxy setting is set in the client, it will be used as well.
        :return: True if internet connection is on; False otherwise.
        """
        try:
            requests.head(self.test_uri, proxies=self.proxies)
            return True
        except requests.ConnectionError:
            return False

    def run(self):
        while True:
            th = self.queue.get()  # blocking call
            while not self.is_connected():
                time.sleep(self.retry_delay)
            self.conditions[th.ident].acquire()
            self.conditions[th.ident].notify()
            self.conditions[th.ident].release()
