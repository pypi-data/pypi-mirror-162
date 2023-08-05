import os

from requests import Response, exceptions, get, post
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class KeycloakContainer(DockerContainer):
    def __init__(self, image="jboss/keycloak:16.1.1", port_to_expose=8080):
        super(KeycloakContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose).with_env(
            "KEYCLOAK_PASSWORD", "admin"
        ).with_env("KEYCLOAK_USER", "admin")

    @wait_container_is_ready(exceptions.ConnectionError)
    def _connect(self):
        print(f"Connecting to keycloak on {self.get_url()}")
        res: Response = get(self.get_url())
        if res.status_code != 200:
            raise Exception()

    def get_url(self):
        port = self.get_exposed_port(self.port_to_expose)
        host = self.get_container_host_ip()
        return f"http://{host}:{port}"

    def start(self):
        super().start()
        self._connect()
        return self

    def _get_keycloak_admin_access_token(self):
        return self.get_access_token(
            username="admin", password="admin", realm="master", client_id="admin-cli"
        )

    def get_access_token(
        self,
        username: str = "admin",
        password: str = "admin",
        realm: str = "master",
        client_id: str = "admin-cli",
    ):
        token_url = (
            f"{self.get_url()}/auth/realms/{realm}/protocol/openid-connect/token"
        )
        token_response: Response = post(
            url=token_url,
            data={
                "username": username,
                "password": password,
                "client_id": client_id,
                "grant_type": "password",
            },
        )
        return token_response.json()["access_token"]

    def create_realm_with_role(self, realm_name: str, role_name: str):
        realm = self.create_realm(name=realm_name)
        if not self.create_role(
            role_name=role_name, role_id=role_name, realm_name=realm_name
        ):
            raise Exception("Failed creating role")
        roles = self.get_roles(realm_name)
        role = None
        for _role in roles:
            if _role["name"] == role_name:
                role = _role
                break
        if role is None:
            raise Exception("Role shall not be none")
        users = self.get_users(realm_name)
        for user in users:
            if not self.set_roles_for_realm(realm_name, user["id"], [role]):
                raise Exception("Failed setting role for user", user["id"])
        return realm

    def create_realm_client(self, realm_name: str, client_id: str) -> bool:
        """create a client for the realm with the provided name"""
        access_token = self._get_keycloak_admin_access_token()
        client_data = {
            "enabled": True,
            "clientId": client_id,
            "protocol": "openid-connect",
            "protocolMappers": [
                {
                    "protocol": "openid-connect",
                    "config": {
                        "id.token.claim": True,
                        "access.token.claim": True,
                        "userinfo.token.claim": True,
                        "usermodel.realmRoleMapping.rolePrefix": "",
                        "multivalued": "",
                        "claim.name": "",
                        "jsonType.label": "",
                    },
                    "name": "role-mapper",
                    "protocolMapper": "oidc-usermodel-realm-role-mapper",
                }
            ],
        }
        response = post(
            f"{self.get_url()}/auth/admin/realms/{realm_name}/clients",
            headers={"Authorization": f"bearer {access_token}"},
            json=client_data,
        )
        return response.status_code == 201

    def get_roles_for_user(self, realm_name: str, user_id: str) -> list:
        """returns a list of assigned roles for a user in a realm"""
        access_token = self._get_keycloak_admin_access_token()
        response = get(
            f"{self.get_url()}/auth/admin/realms/{realm_name}/users/{user_id}/role-mappings/realm",
            headers={"Authorization": f"bearer {access_token}"},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def create_role(self, role_name: str, role_id: str, realm_name: str) -> bool:
        access_token = self._get_keycloak_admin_access_token()

        role_json = {
            "id": role_id,
            "name": role_name,
        }

        response = post(
            f"{self.get_url()}/auth/admin/realms/{realm_name}/roles",
            json=role_json,
            headers={"Authorization": f"bearer {access_token}"},
        )
        return response.status_code == 201

    def get_roles(self, realm_name: str) -> list:
        """
        returns a list of roles for the specified realm
        ---------
        a role is a dict of this shape
        {
            "id": str #id of that role>,
            "name": str #name of that role>,
            "composite": bool,
            "clientRole": bool,
            "containerId": str
        }
        """
        access_token = self._get_keycloak_admin_access_token()

        response = get(
            f"{self.get_url()}/auth/admin/realms/{realm_name}/roles",
            headers={"Authorization": f"bearer {access_token}"},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def set_roles_for_realm(self, realm_name: str, user_id: str, roles: list) -> bool:
        """
        applies a list of roles for the specified user in the specified realm
        ---------
        returns if operation was succesful
        """
        access_token = self._get_keycloak_admin_access_token()
        response = post(
            f"{self.get_url()}/auth/admin/realms/{realm_name}/users/{user_id}/role-mappings/realm",
            json=roles,
            headers={"Authorization": f"bearer {access_token}"},
        )
        return response.status_code == 204

    def get_users(self, realm_name: str) -> list:
        """
        returns a list of users this realm has
        ---------
        a user is a dict of this shape
        {
            "id": str #id of user,
            "username": str #name of use,
            "enabled": bool #determine if user is enabled,
            "totp": bool,
            "emailVerified": bool,
            "firstName": str,
            "lastName": str,
            "disableableCredentialTypes": list,
            "requiredActions": list,
            "notBefore": 0,
            "access": {
                "manageGroupMembership": bool,
                "view": bool,
                "mapRoles": bool,
                "impersonate": bool,
                "manage": bool
            }
        }
        """
        access_token = self._get_keycloak_admin_access_token()

        response = get(
            f"{self.get_url()}/auth/admin/realms/{realm_name}/users",
            headers={"Authorization": f"bearer {access_token}"},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def create_realm(self, name: str):

        access_token = self._get_keycloak_admin_access_token()

        realm_json = {
            "realm": name,
            "displayName": name,
            "enabled": True,
            "users": [
                {
                    "enabled": True,
                    "firstName": name,
                    "lastName": name,
                    "username": name,
                    "credentials": [
                        {"temporary": False, "type": "password", "value": "test"}
                    ],
                }
            ],
        }

        response = post(
            f"{self.get_url()}/auth/admin/realms",
            json=realm_json,
            headers={"Authorization": f"bearer {access_token}"},
        )
        realm_response = get(
            response.headers["Location"],
            headers={"Authorization": f"bearer {access_token}"},
        )
        realm = realm_response.json()
        url = f'{self.get_url()}/auth/realms/{realm["realm"]}'

        if not self.create_realm_client(name, "role-cli"):
            raise Exception("Failed creating role client")

        return {"realm": realm, "url": url}
