from myst.client import Client
from myst.openapi.models.alias_get import AliasGet


def request_sync(client: Client, node_uuid: str) -> AliasGet:
    """Create an alias for the node."""

    return client.request(method="post", path=f"/alias/-/node/{node_uuid}", response_class=AliasGet)
