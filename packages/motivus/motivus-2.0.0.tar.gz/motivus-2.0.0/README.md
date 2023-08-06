# Motivus framework

This package contains:

- A CLI utility to manage:
  - Algorithm compilation
  - Version registry uploads to Motivus marketplace
- A Client library to use Motivus cluster nodes

# Installation
```sh
$ pip install motivus
```

# Configuration
Configuration is provided through environment variables. You can also create a `.env` file.

```sh
# .env
# for consuming algorithms from Motivus marketplace repository and sending tasks to Motivus cluster
APPLICATION_TOKEN=MWBatxipDHG4daX3ebBPyWDj36AsWqbOJc=
WEBSOCKET_URI=wss://waterbear.api.motivus.cl/client_socket/websocket

# for pushing algorithm versions to Motivus marketplace repository
MOTIVUS_PERSONAL_ACCESS_TOKEN=MWBpatrZpMb1vD_QwAro=
```

## CLI
### Create a new project

Docker required

```sh
$ motivus new ALGORITHM_NAME
```

Creates a new Rust project.
### Compilation

Docker required

TODO: add compilation process description

```sh
$ motivus build -h
```

### Upload new version

Uploads packaged algorithm version contents to Motivus marketplace

Authentication is provided through env value

```environ
MOTIVUS_PERSONAL_ACCESS_TOKEN=MWBpatxipsWqbOJc=
```

```sh
$ motivus push -h
```

### Worker for local development

Docker required

Start a worker in loopback mode, useful for local algorithm development
```sh
$ motivus loopback -h
```

### Worker

Docker required

Start a worker that connects to Motivus cluster.
```sh
$ motivus worker -h
```



## Client
### Basic task execution example
Set your application token as an environment value as follows:
```environ
APPLICATION_TOKEN=MWBatxipD4Dj36AsWqbOJc=
```
Execute some tasks, i.e. the "example" algorithm on Motivus marketplace repository.

```python
from motivus.client import Client

conn = await Client.connect()

task_def = {
  "algorithm": "example",
  "algorithm_version": "1.0.0",
  # this would run the equivalent to " $ example 1 3 " on a Motivus worker
  "arguments": [1, 3]
}
task_id = conn.call_async(task_def)
task = conn.select_task(task_id)
result = await task
```

## Getting help
You can contact us anytime using our [contact form](https://motivus.cl/contact/).
