from myst.client import Client
from myst.openapi.models.alias_get import AliasGet


def request_sync(client: Client, alias_uuid: str, project_uuid: str) -> AliasGet:
    """Update an alias to point to a different project."""

    return client.request(method="post", path=f"/alias/{alias_uuid}/project/{project_uuid}", response_class=AliasGet)
