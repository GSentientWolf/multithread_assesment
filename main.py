
"""
  Demonstration main file
"""

import time
from logger.logger import MyLogger
from sensors.sensor import get_sensor, SensorType
from service.repository.repository import FileRepository
from utils.network import Network

if __name__ == '__main__':

    logging = MyLogger()
    network = Network()
    repository = FileRepository(location='./file_repo.txt', network=network)
    thermal_sensor_05 = get_sensor(sensor_type=SensorType.THERMAL,
                                   sensor_name='Thermal Sensor AZ01',
                                   net=network,
                                   exec_interval=3.2)
    vibration_sensor_02 = get_sensor(sensor_type=SensorType.VIBRATION,
                                     sensor_name='Vibration Sensor AZ01',
                                     net=network,
                                     exec_interval=1.2)
    pressure_sensor_99 = get_sensor(sensor_type=SensorType.PRESSURE,
                                    sensor_name='Pressure Sensor AZ01',
                                    net=network,
                                    exec_interval=4.6)
    magnetic_sensor_11 = get_sensor(sensor_type=SensorType.THERMAL,
                                    sensor_name='Magnetic Sensor AZ01',
                                    net=network,
                                    exec_interval=1)
    humidity_sensor = get_sensor(sensor_type=SensorType.THERMAL,
                                 sensor_name='Humidity Sensor AZ01',
                                 net=network,
                                 exec_interval=2.8)
    network.start_network()
    repository.start_repository()
    logging.add_sensors([
        thermal_sensor_05,
        pressure_sensor_99,
        humidity_sensor,
        magnetic_sensor_11,
        vibration_sensor_02
    ])
    logging.start_bank()
    time.sleep(40)
    logging.stop_bank()
    repository.stop_repository()
    network.stop_network()
