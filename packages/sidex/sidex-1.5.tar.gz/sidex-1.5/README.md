# Simple Data Exchange server over HTTP
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/sidex/badge/?version=latest)](https://sidex.readthedocs.io/en/latest/?badge=latest)

## Overview
This package provides a function to launch a simple file server. Getting, putting, and deleting files on the server via the HTTP POST methods are available. The function `setup_sidex()` returns a `flask` instance. You can launch a simple file server by `run()`.

``` python
from sidex import setup_sidex

target = '/path/to/directory'
app = setup_sidex(target)
app.run()
```

Otherwise, you can directly call `sidex.server`.

``` sh
$ python -m sidex.server /path/to/directory
```

By default, only retrieving files (`get`) is available. The `put` and `delete` methods are enabled by setting a 'token' for each method. Of course, the `get` function can be restricted by a `token`.

The HTTP POST method is available to submit a request. Any request should contain the `method` field, which should be one of `get`, `put`, and `delete`. The `token` field may be required in some cases. The followings are samples with `curl`.

``` sh
$ curl http://0.0.0.0:8080/path/to/file -F 'method=get'
$ curl http://0.0.0.0:8080/path/to/upload -F 'method=put' -F 'payload=@filename' -F 'token=foo'
$ curl http://0.0.0.0:8080/path/to/delete -F 'method=delete' -F 'token=bar'
```

The package provides a function, `sidex_request()`, which is a wrapper function of `requests.post()`. You can directly execute `sidex.client`.

``` sh
$ python -m sidex.client http://0.0.0.0:8080/path/to/file
$ python -m sidex.client http://0.0.0.0:8080/path/to/file --ping
$ python -m sidex.client http://0.0.0.0:8080/path/to/upload -f upload_file
$ python -m sidex.client http://0.0.0.0:8080/path/to/delete -d
```


## Dependencies
The library is developed on Python 3.9.9. The following packages are required:

``` python
flask>=2.0
requests>=2.27
```
