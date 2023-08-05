from datetime import datetime
from factoree_ai_connectors.sensor.sensor_info import SensorInfo


def get_silver_file_name(sensor_info: SensorInfo, first_sample: datetime, last_sample: datetime) -> str:
    file_base_name = f'{sensor_info.facility}-{sensor_info.sensor_type}-{sensor_info.tag_id}'
    first_sample_display = first_sample.strftime("%Y_%m_%dT%H_%M_%S%z").replace("+", "_")
    last_sample_display = last_sample.strftime("%Y_%m_%dT%H_%M_%S%z").replace("+", "_")
    return f'input/{sensor_info.data_type}/{file_base_name}.{first_sample_display}-{last_sample_display}.json'
