from myst.client import Client
from myst.openapi.models.permission_list import PermissionList
from myst.openapi.models.shareable_resource_unshare import ShareableResourceUnshare


def request_sync(client: Client, uuid: str, json_body: ShareableResourceUnshare) -> PermissionList:

    return client.request(
        method="post", path=f"/projects/{uuid}:unshare", response_class=PermissionList, request_model=json_body
    )
