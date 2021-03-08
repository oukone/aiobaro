import functools

from .tools import login_required, matrix_client


class MatrixAdminClient:

    admin_root = "/_synapse/admin/v2/"

    def __init__(
        self,
        homeserver: str,
        access_token: str = None,
        client=matrix_client,
    ):
        self.homeserver = homeserver
        self.access_token = access_token
        self.client = functools.partial(
            matrix_client,
            self.admin_path,
            access_token=self.access_token,
        )

    @property
    def admin_path(self):
        return f"{self.homeserver.strip('/')}/_synapse/admin/v2/"

    async def reset_password(self, user_id: str, password: str, **kwargs):
        return await self.client(
            "POST",
            f"reset_password/{user_id}",
            json={
                "new_password": password,
                "logout_devices": True,
            },
            **kwargs,
        )

    async def list_users(self, limit: int, start_from: int, **kwargs):
        kwargs["params"] = {
            **kwargs["params"],
            "from": start_from,
            "limit": limit,
        }
        return await self.client("GET", "users", **kwargs)
