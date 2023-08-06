# SensorNet
> Lightweight sensor status pulling daemon.

![PythonSupport](https://img.shields.io/static/v1?label=Python&message=3.10&color=blue&style=flat&logo=python)
[![PyPI](https://img.shields.io/pypi/v/SensorNet)](https://pypi.org/project/SensorNet/)
![VersionStatus](https://img.shields.io/pypi/status/SensorNet)
[![codecov](https://codecov.io/gh/HanaPoulpe/SensorNet/branch/master/graph/badge.svg?token=9B5E336IZW)](https://codecov.io/gh/HanaPoulpe/SensorNet)
![Checks](https://img.shields.io/github/checks-status/hanapoulpe/SensorNet/master)

## Installation:

```pip install SensorNet```

## Run instructions:

1) Run once: ```sensornet -c <path/to/config.yaml>```
2) Run daemon: ```sensornet -d - c <path/to/config.yaml>```

## Configuration:

Create a configuration file in ```/etc/sensornet/sensor.yaml```

```yaml
daemon_name: SensorNetDaemon
backend:
  driver: sqlalchemy
  url: "engine://username:password@host:port/dbname"
networks:
  - name: network0
    ip_addresses:
      - 10.0.0.1/32
      - 10.0.1.10 - 10.0.1.20
    sensor_prefix: sn0
    api_port: 80
    api_location: "/"
    cron: "* * * * * *"
```

### daemon_name
Name for the daemon that will be sent to the backend.

### backend
*driver:* name of the backend module to use. Modules should be installed in ```/lib/sensor_net/backend_driver/module.py```

This section will contain the module configuration, and will be passed as a dict to the get_driver function.

```python
SensorData = namedtuple('SensorData', ["name", "value", "datetime_utc"])

class BackendDriver(Protocol):
    def write(self, network_name: str, network_prefix: str, sensor_address: str, data: list[SensorData]):
        """Writes all data to the backend"""
        ...

def get_driver(name: str, configuration: dict) -> BackendDriver:
    """Instantiate a new BackendDriver from the given configuration"""
    raise NotImplementedError("get_backend is not implemented.")

```

*Note: get_driver **MUST** have parameters types annotations.*

### networks:
Defines the networks to pull.

A pull is a simple HTTP GET request to ```http://endpoint/api_location```
It expects a JSON body containing:

```json
{
  "data": [
    {
      "name": str,
      "value": number,
      "epoch": number
    }, ...
  ]
}
```

- *network_name:* the name of the network
- *ip_addresses:* IP address with mask or range of IP addresses
- *sensor_prefix:* prefix for the sensor, it's recommended to use the sensor prefix for deduplication in the backend.
- *api_port:* port the API is listening to.
- *api_location:* location of the sensor API
- *cron:* interval between polling for this network
