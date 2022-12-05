"""
    BaseSensor subclassed from threading.Thread
"""

import json
import time
import threading
from datetime import datetime
from typing import Union, Callable, Tuple, Iterator
from utils.network import Network
from service.model.messages import DeviceMessage, DeviceMessageEnum
from service.repository.repository import FileRepository
from sensors.signal import Signal


BASE_INTERVAL = 5.0
START_STOP_WAIT = 2.0
TS_FORMAT = 6
DEVICE = 1
INDEX = 0
N_MAX_SENSORS = 5


# class Network:
#      ...


class BaseSensor(threading.Thread):
    """ Base class for any sensor type"""

    def __init__(self, *, name: str, net: Network,
                 interval: float = BASE_INTERVAL):
        """ Initialize with required named parameters """
        super().__init__(name=name, daemon=True, target=self.run)
        self.device_name = name
        self.interval = interval
        self.signal = Signal(name)
        self.value = None
        self.connection_point = net.connect_device()
        self.lock = threading.Lock()
        self.start_running = threading.Event()

    def _build_sensor_message(self) -> dict:
        """
        This property provides the sensor message's main body
        :return: Updated json readout for the sensor.
        """
        printable_keys = {'device_name', 'value'}
        out = {k: v for k, v in self.__dict__.items() if k in printable_keys}
        out.update({'interval': f'{1000 * self.interval} ms'})
        out.update({'posix_timestamp':
                        f'{datetime.now().timestamp():.{TS_FORMAT}f}'})
        return out

    @property
    def readout(self) -> DeviceMessage:
        """
        This property updates the sensor value and provides the sensor message's
        main body.
        :return: Updated json readout for the sensor.
        """
        self.value = self.signal.value
        out = self._build_sensor_message()
        out = {'readout': out}
        msg_content = json.dumps(out)
        return DeviceMessage(str(DeviceMessageEnum['DEVICE_READOUT'].value),
                             msg_content)

    def get_readout(self) -> DeviceMessage:
        return self.readout

    @property
    def connection_point(self) -> callable:
        """ Returns the stored logger callback function """
        return self._readout_callback_fn

    @connection_point.setter
    def connection_point(self, fn: Union[Callable[[...], None] | None]) -> None:
        """ Stores de callback function when the sensor is registered """
        self._readout_callback_fn = fn

    def send_readout(self, readout: DeviceMessage) -> None:
        """
        Sends sensor readout to the logger module via the provided callback
        function
        """
        # The read property readout
        self.connection_point(readout)

    def start_sensor(self) -> None:
        if not self.is_alive():
            # Activate the thread
            print(f'Starting the thread: {self.name} for {self.device_name}')
            self.start()
            self.start_running.set()
            time.sleep(START_STOP_WAIT)
            return
        print(f'The thread {self.name} is already running!')

    def stop_sensor(self) -> None:
        if not self.is_alive():
            return
        self.start_running.clear()
        self.join(1.5 * self.interval)
        if self.is_alive():
            print(f'Thread {self.name} is still running!')
        else:
            print(f'Thread {self.name} has stopped!')

    def run(self):
        """
        Thread's worker function
        :return: None
        """
        timer = self.interval
        self.start_running.wait()
        while self.start_running.is_set():
            time.sleep(timer)
            with self.lock:
                readout = self.get_readout()
                self.send_readout(readout)
                print(readout)


class SensorBank:
    """
    Hold up to five sensors
    """
    def __init__(self) -> None:
        self.sensors = []

    def __iter__(self) -> Iterator:
        return iter(self.sensors)

    def __len__(self) -> int:
        return len(self.sensors)

    def sensor_names(self):
        return [sensor.device_name for sensor in self]

    def add_sensors(self, sensors: Union[Tuple[BaseSensor]|list[BaseSensor]]) -> None:
        """
        Add a list of sensors
        :param sensors:
        :return:
        """
        for sensor in sensors:
            if len(self) > N_MAX_SENSORS:
                print(f'Bank limit reached: {N_MAX_SENSORS} sensors max.')
                break
            self.sensors.append(sensor)

    def remove_by_name(self, sensor_name: str) -> None:
        """
        Remove Sensor device from the bank and stop it's thread
        :param sensor_name: Device's name
        :return: None
        """
        device_index, device = self.find_by_name(sensor_name)
        self.sensors.pop(device_index)
        device.stop_sensor()

    def find_by_name(self, sensor_name: str) -> Tuple[Union[int|None],
                                                      Union[BaseSensor | None]]:
        """
        Find sensor device identified by "sensor_name"
        :param sensor_name: str
        :return: device_index, device
        """
        names = [sensor.device_name for sensor in self]
        if sensor_name not in names:
            print(f'Sensor: {sensor_name} is not in this bank')
            return None, None
        device_index = self.sensors.index(sensor_name)
        return device_index, self.sensors[device_index]

    def start_sensor_by_name(self, sensor_name: str) -> None:
        """
        Start Sensor device from it's name
        :param sensor_name:
        :return:
        """
        device_index, device = self.find_by_name(sensor_name)
        if device_index is None:
            print(f'Sensor device {sensor_name} is not present in the bank')
            return
        device.start_sensor()

    def start_by_index(self, index: int) -> None:
        """
        Start a specific sensor identified by index
        :param index:
        :return:
        """
        try:
            device = self.sensors[index]
        except IndexError:
            print(f'Invalid index. Maximum index is {N_MAX_SENSORS - 1}')
        else:
            device.start_sensor()

    def stop_by_index(self, index: int) -> None:
        """
        Start a specific sensor identified by index
        :param index:
        :return:
        """
        try:
            device = self.sensors[index]
        except IndexError:
            print(f'Invalid index. Maximum index is {N_MAX_SENSORS - 1}')
        else:
            device.stop_sensor()

    def start_bank(self) -> None:
        """
        Start all devices present at the bank
        :return:
        """
        for sensor in self:
            sensor.start_sensor()

    def stop_bank(self) -> None:
        """
        Stop all devices present at the bank
        :return:
        """
        for sensor in self:
            sensor.stop_sensor()


if __name__ == "__main__":

    #n = Network(repository=repo)
    network = Network()
    repo = FileRepository(location='./test_sensors.txt', network=network)
    s1 = BaseSensor(name='Thermal Sensor 01', network=network, interval=2.0)
    s2 = BaseSensor(name='Thermal Sensor 02', network=network, interval=2.5)
    s3 = BaseSensor(name='Thermal Sensor 03', network=network, interval=3.0)
    s4 = BaseSensor(name='Thermal Sensor 04', network=network, interval=1.0)
    s5 = BaseSensor(name='Thermal Sensor 05', network=network, interval=1.5)
    bank = SensorBank()
    bank.add_sensors([
        s4,
        s5,
        s1,
        s2,
        s3
    ])
    bank.start_bank()
    time.sleep(30)
    bank.stop_bank()
