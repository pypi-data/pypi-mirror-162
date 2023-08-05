from dataclasses import dataclass


@dataclass
class SensorInfo:
    company: str
    site: str
    data_type: str
    facility: str
    sensor_type: str
    tag_id: str
