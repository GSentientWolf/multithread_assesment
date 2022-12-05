"""
  Logger. This is an implementation of the observer pattern.
  It should handle the construction of the Sensor messages and the
  output to the repository.

  :TODO Should be non blocking. This part should be done with asyncio on the sensors
  Non-blocking threads are dangerous. This should be implemented with multiprocessing
  instead
"""

import threading
import time
from queue import Queue
from typing import List, Callable


N_MESSAGES = 5
DEFAULT_WAIT = 1            # Wait at most 1 sec
START_STOP_WAIT = 2         # 2 s
NETWORK_INTERVAL = 0.5      # 500 ms
NETWORK_START_WAIT = 5      # 5 s


class Network(threading.Thread):
    """
    Logging service for devices and repository
    """

    def __init__(self):
        super().__init__(name='Network', target=self.run,
                         daemon=True)
        self.lock = threading.Lock()
        self.message_queue = Queue(maxsize=3*N_MESSAGES)
        self.devices = dict()
        self.notify_repo = None
        self.start_running = threading.Event()

    def start_network(self) -> None:
        if not self.is_alive():
            # Activate the thread
            print(f'Starting the thread: {self.name}')
            self.start()
            self.start_running.set()
            time.sleep(START_STOP_WAIT)
            return
        print(f'The thread {self.name} is already running!')

    def stop_network(self) -> None:
        if not self.is_alive():
            return
        self.start_running.clear()
        self.join(1.5 * NETWORK_INTERVAL)
        if self.is_alive():
            print(f'Thread {self.name} is still running!')
        else:
            print(f'Thread {self.name} has stopped!')

    def send(self, message: str) -> None:
        """
        All Sensor devices place their messages into a thread safe queue.
        The access is provided by setting this function as a callback to each sensor
        :param message: SensorDeviceMessage
        :return: None
        """
        with self.lock:
            print("Inserting message into the queue")
            self.message_queue.put_nowait(message)

    def get(self) -> List[str]:
        """
        Extract the readout messages from the Sensor devices placed into the queue
        in groups of N_MESSAGES
        :return:
        """
        result = []
        # with self.lock:
        print("Storing messages into repository")
        for _ in range(self.message_queue.qsize()):
            item = self.message_queue.get_nowait()
            result.append(item)
        return result

    def connect_device(self) -> Callable:
        """
        Subscription method to the logger
        :return: returns the function to access the queue
        """
        # Provide the callback function to the device
        return self.send

    def connect_repository(self, notification_fn: Callable) -> Callable:
        """
        Subscribe the repository
        :return: returns the function to get data from the queue
        """
        self.notify_repo = notification_fn
        return self.get

    def notify_repository(self) -> None:
        self.notify_repo()

    def run(self) -> None:
        self.start_running.wait()
        while self.start_running.is_set():
            time.sleep(NETWORK_INTERVAL)
            with self.lock:
                self.notify_repository()
