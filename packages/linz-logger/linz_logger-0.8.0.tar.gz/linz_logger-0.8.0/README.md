# Python LINZ Logger

[![GitHub Actions Status](https://github.com/linz/python-linz-logger/workflows/Build/badge.svg)](https://github.com/linz/python-linz-logger/actions)
[![Kodiak](https://badgen.net/badge/Kodiak/enabled?labelColor=2e3a44&color=F39938)](https://kodiakhq.com/)
[![Dependabot Status](https://badgen.net/badge/Dependabot/enabled?labelColor=2e3a44&color=blue)](https://github.com/linz/python-linz-logger/network/updates)
[![License](https://badgen.net/github/license/linz/python-linz-logger?labelColor=2e3a44&label=License)](https://github.com/linz/python-linz-logger/blob/master/LICENSE)
[![Conventional Commits](https://badgen.net/badge/Commits/conventional?labelColor=2e3a44&color=EC5772)](https://conventionalcommits.org)
[![Code Style](https://badgen.net/badge/Code%20Style/black?labelColor=2e3a44&color=000000)](https://github.com/psf/black)

## Why?

LINZ has a standard logging format based loosely on the [pinojs](https://github.com/pinojs/pino) logging format:

```json
{
  "level": 30,
  "time": 1571696532994,
  "pid": 10671,
  "hostname": "Ubuntu1",
  "id": "01DQR6KQG0K60TP4T1C4VC5P74",
  "msg": "SomeMessage",
  "v": 1
}
```

## Usage

```
pip install --upgrade linz-logger
```

```python
from os import environ

from linz_logger import get_log, set_level, LogLevel

set_level(LogLevel[environ.get("LOGLEVEL", "WARNING").lower()].value)
set_contextvars({"hostname": environ.get("HOSTNAME")}) # remove_contextvars(["hostname"]) to remove a key
get_log().error('Hello World', key="value")
# {"key": "value", "level": 50, "time": 1601555605017, "v": 1, "pid": 311800, "msg": "Hello World", "hostname": "Ubuntu1"}
```
