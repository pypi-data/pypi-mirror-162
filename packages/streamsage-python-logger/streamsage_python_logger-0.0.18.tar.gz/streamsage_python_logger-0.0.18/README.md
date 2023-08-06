# STREAM SAGE PYTHON LOGGER

## Log format

```shell
[<Date> <Time>][<logLevel>][<context>][<file>:<line>][<LoggerOptionalParams>] <message>
```

Date format: `YYYY-MM-DD`<br/>
Time format: `HH:mm:ss`


## Logger output

```shell
[2022-04-15 12:06:34][info][Sample App][samle_file.py:1] Sample LOG message
[2022-04-15 03:06:00][info][Sample App][samle_file.py:1][messageId:some-message-id][domain:message-domain] Sample LOG message with additional params
[2022-04-15 12:06:34][error][Sample App][samle_file.py:1][customer:customer] Sample ERROR message with additional params
[2022-04-15 21:43:36][debug][Sample App][samle_file.py:1][debugLevel:5] Sample Debug message in debug level 5
[2022-04-15 10:20:28][debug][Sample App][samle_file.py:1][debugLevel:2] Sample Debug message in debug level 2
```

# Installation

Add `streamsage-python-logger==0.0.17` to requirements.txt or install via pip:
```shell
pip install streamsage-python-logger==0.0.17
```

# Environments

| Variable               | Description                                                        | Default | Supported |
| ---------------------- | ------------------------------------------------------------------ | ------- | --------- |
| `LOG_SDK_NO_COLOR`     | Set to any value to disable logs colorizing                        | -       | -         |
| `LOG_SDK_TRANSPORTS `  | Comma separated list of log transporters that will be used by app. | -       | `fluent`  |
| `LOG_SDK_SERVICE_NAME` | Service name that will be included in message payload.             | -       | -         |


### **Logger options:**

**Required:**

- `context` - The context of logger instance.

**Optional:**

- `level` - Enable logger via passing a log level: `fatal`, `error`, `warn`, `info`, `debug`, `trace` or `false` if it should
  be disabled. **Default: `info`**
  Then, you can use following methods `log()`, `fatal()`, `error()`, `warn()`, `info()`, `debug()`, `trace()`:
- `log()` - displays message in given log level.
- `fatal()` - displays message in `fatal` log level.
- `error()` - displays message in `error` log level.
- `warn()` - displays message in `warn` log level.
- `info()` - displays message in `info` log level.
- `debug()` - displays message in `debug` log level.
- `trace()` - displays message in `trace` log level.

## Available transports

Below has been describe all currently supported transport by the Logger.

### Console

> **Notice:** Console transport is always enabled.

| Variable                          | Description              | Default | Supported                                          |
| --------------------------------- | ------------------------ | ------- | -------------------------------------------------- |
| `LOG_SDK_TRANSPORT_CONSOLE_LEVEL` | Logging level to console | `info`  | `fatal`, `error`, `warn`, `info`, `debug`, `trace` |

### Fluent

| Variable                                      | Description                                      | Default | Supported                                          |
| --------------------------------------------- | ------------------------------------------------ | ------- | -------------------------------------------------- |
| `LOG_SDK_TRANSPORT_FLUENT_LEVEL`              | Logging level to FluentD                         | `info`  | `fatal`, `error`, `warn`, `info`, `debug`, `trace` |
| `LOG_SDK_TRANSPORT_FLUENT_URL`                | URL of the FluentD server                        | -       | -                                                  |
| `LOG_SDK_TRANSPORT_FLUENT_TIMEOUT`            | Timeout for response from the FluentD server.    | `3000`  | -                                                  |

# Logger sample usage

Logger can be initialized by `get_logger()` method:
```python
from streamsage_python_logger.streamsage_logger import get_logger

logger = get_logger("SomeApp")
```

for implementing logger with other libraries use `LoggerConfig` class with logging `dictConfig` e.g. on FastApi and uvicorn server:

```python
import uvicorn
from fastapi import FastAPI
from logging.config import dictConfig
from streamsage_python_logger.streamsage_logger import LoggerConfig

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080,
                access_log=False,
                log_config=dictConfig(LoggerConfig(context='SomeApp').dict()),
                log_level='info')
```