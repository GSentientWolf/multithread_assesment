"""
  Logger. This is an implementaiton of the observer pattern.
  It should handle the construction of the Senssor messages and the
  output to the repository.

  :TODO Should be non blocking. This part should be done with asyncio on the sensors
  Non-blocking threads are dangerous. This should be implemented with multiprocessing
  instead
"""

import threading
from typing import Union, List, Iterator, Tuple
#from service.repository.repository import Repository
from sensors.basesensor import BaseSensor
#from utils.network import Network
#from service.model.messages import Message


N_MESSAGES = 5
DEFAULT_WAIT = 1            # Wait at most 1 sec
N_MAX_SENSORS = 5


class MyLogger:
    """
    Hold up to five sensors
    """
    def __init__(self, *, name='Logger') -> None:
        self.name = name
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
