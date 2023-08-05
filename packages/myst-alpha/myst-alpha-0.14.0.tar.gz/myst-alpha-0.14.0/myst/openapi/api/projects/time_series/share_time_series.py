from myst.client import Client
from myst.openapi.models.permission_list import PermissionList
from myst.openapi.models.shareable_resource_share import ShareableResourceShare


def request_sync(client: Client, project_uuid: str, uuid: str, json_body: ShareableResourceShare) -> PermissionList:

    return client.request(
        method="post",
        path=f"/projects/{project_uuid}/time_series/{uuid}:share",
        response_class=PermissionList,
        request_model=json_body,
    )
