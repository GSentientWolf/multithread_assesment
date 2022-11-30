
from enum import Enum
from typing import Union
from sensors.basesensor import BaseSensor
from sensors.basesensor import SensorBank

#from utils.network import Network


class Network:
    ...


class SensorType(Enum):
    THERMAL = 'Thermal'
    HUMIDITY = 'Hygrometer'
    VIBRATION = 'Vibration'
    MAGNETIC = 'Magnetic'
    PRESSURE = 'Pressure'


class Sensor(BaseSensor):
    """
    Generic Sensor definition
    """
    def __init__(self, *, sensor_type: SensorType, name: str, network: Network,
                 interval: Union[int | float]) -> None:
        sensor_types = {name: member.value for name, member in
                        SensorType.__members__.items()}
        sensor_type = sensor_types[sensor_type.name]
        super().__init__(name=name, network=network, interval=interval)
        self.sensor_type = sensor_type

    def _build_sensor_message(self) -> dict:
        out = {'sensor_type': self.sensor_type}
        out.update(super()._build_sensor_message())
        return out


def get_sensor(*, sensor_type: SensorType, sensor_name: str,
               network: Network, exec_interval: float) -> Sensor:
    """
    Sensor factory function
    :param sensor_type: SensorType
    :param sensor_name: str
    :param exec_interval: float
    :param network: Network
    :return:
    """
    generic_sensor = Sensor(name=sensor_name, sensor_type=sensor_type,
                            network=network, interval=exec_interval)
    return generic_sensor


if __name__ == '__main__':

    import time

    n = Network()
    thermal_01 = get_sensor(sensor_type=SensorType.THERMAL,
                            sensor_name='Thermal Sensor 01', network=n,
                            exec_interval=2.0)
    magnetic_01 = get_sensor(sensor_type=SensorType.MAGNETIC,
                             sensor_name='Magnetic Sensor 02',
                             network=n, exec_interval=2.5)
    vibration_01 = get_sensor(sensor_type=SensorType.VIBRATION,
                              sensor_name='Vibration Sensor 01',
                              network=n, exec_interval=3.0)
    hygrometer_01 = get_sensor(sensor_type=SensorType.HUMIDITY,
                               sensor_name='Humidity Sensor 04',
                               network=n, exec_interval=1.0)
    pressure_01 = get_sensor(sensor_type=SensorType.PRESSURE,
                             sensor_name='Vibration Sensor 03',
                             network=n, exec_interval=1.5)
    bank = SensorBank()
    bank.add_sensors([
        pressure_01,
        vibration_01,
        hygrometer_01,
        thermal_01,
        magnetic_01
    ])
    bank.start_bank()
    time.sleep(30)
    bank.stop_bank()
