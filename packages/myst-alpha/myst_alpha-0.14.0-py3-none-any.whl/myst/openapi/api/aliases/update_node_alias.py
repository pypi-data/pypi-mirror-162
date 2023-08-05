from myst.client import Client
from myst.openapi.models.alias_get import AliasGet


def request_sync(client: Client, alias_uuid: str, node_uuid: str) -> AliasGet:
    """Update an alias to point to a different node."""

    return client.request(method="post", path=f"/alias/{alias_uuid}/node/{node_uuid}", response_class=AliasGet)
