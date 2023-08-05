from myst.client import Client
from myst.openapi.models.alias_get import AliasGet


def request_sync(client: Client, project_uuid: str) -> AliasGet:
    """Create an alias for the project."""

    return client.request(method="post", path=f"/alias/-/project/{project_uuid}", response_class=AliasGet)
