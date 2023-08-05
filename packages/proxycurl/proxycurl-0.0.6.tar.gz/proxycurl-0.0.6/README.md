# Usage
To generate the library you must run this following command:
```console
./codegen/generator
```

* Make sure you change the `PROXYCURL_API_KEY` in `proxycurl/config.py`

# Example
After you generate the library you can use like the example that provided each concurrent method:

## Gevent
```console
poetry run python examples/lib-gevent.py
```
## Twisted
```console
poetry run python examples/lib-twisted.py
```
## Asyncio
```console
poetry run python examples/lib-asyncio.py
```