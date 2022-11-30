from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import validates
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Message(Base):
    """
        DB model for sensor readings
    """

    __tablename__ = 'messages'

    timestamp = Column(DateTime, primary_key=True)
    id = Column(Integer)
    sensor_name = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)
    value = Column(Integer, nullable=False)

    def __init__(self, timestamp: datetime, id: int, sensor_name: str,
                 sensor_type: str, value: int) -> None:
        super(Message, self).__init__()
        self.timestamp = timestamp
        self.id = id
        self.sensor_name = sensor_name
        self.sensor_type = sensor_type
        self.value = self.validate_value('value', value)

    @validates('value')
    def validate_value(self, key, value) -> int:
        assert -100 <= value <= 100, f"ERROR: valor out of range :{value}"
        return value
