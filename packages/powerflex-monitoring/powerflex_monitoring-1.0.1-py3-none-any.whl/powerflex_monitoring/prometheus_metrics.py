from prometheus_client.asgi import make_asgi_app


# The prometheus_client library has no type hints.
def make_metrics_app():  # type: ignore
    return make_asgi_app()
