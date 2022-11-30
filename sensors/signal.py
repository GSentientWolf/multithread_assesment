''' Synthetic signal module '''
import random
from random import gauss

# Sensor MIN and MAX ranges
SENSOR_MAX = 100
SENSOR_MIN = -100
N_DECIMALS = 4
MU = 0
MAIN_VARIANCE = 24.5
MINOR_VARIANCE = 0.6


class Signal:
    ''' Main class for a synthetic signal (a Gaussian process) '''
    def __init__(self, initial_value: str) -> None:
        self.current_value = None
        self.value = initial_value
        self.n_decimals = N_DECIMALS

    @property
    def value(self) -> str:
        delta = gauss(MU, MINOR_VARIANCE)
        self.current_value = self._value + delta
        if self.current_value < SENSOR_MIN:
            self._value += (-1.0 if delta < 0 else 1.0) * delta
            self.current_value += 4 * delta
        elif self.current_value > SENSOR_MAX:
            self._value -= (-1.0 if delta < 0 else 1.0) * delta
            self.current_value += 4 * delta
        else:
            self._value = self.current_value
        return f'{self.current_value:.{self.n_decimals}f}'

    @value.setter
    def value(self, value: str) -> None:
        random.seed(value)
        self._value = None
        if self.current_value is None:
            self._value = gauss(MU, MAIN_VARIANCE)
    
    def __str__(self):
        return f'{self.value:.{self.n_decimals}f}'

    


