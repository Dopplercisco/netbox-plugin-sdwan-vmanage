"""Cisco vManage SD-WAN API client.

Implements the same API calls used by the existing automation scripts.
TLS verification is intentionally disabled (verify=False) for compatibility
with self-signed vManage certificates; isolate VERIFY_TLS here for easy
improvement later.
"""
import urllib3

import requests

# Single place to control TLS verification. Set to True in production when
# a valid certificate is available.
VERIFY_TLS = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SDWANClient:
    """Object-oriented client for the Cisco vManage REST API."""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = VERIFY_TLS

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def login(self):
        """Authenticate with vManage and store the XSRF token."""
        login_url = f'{self.base_url}/j_security_check'
        payload = {
            'j_username': self.username,
            'j_password': self.password,
        }
        resp = self.session.post(login_url, data=payload)
        resp.raise_for_status()

        token_url = f'{self.base_url}/dataservice/client/token'
        token_resp = self.session.get(token_url)
        if token_resp.status_code == 200 and token_resp.text.strip():
            self.session.headers.update({'X-XSRF-TOKEN': token_resp.text.strip()})

    # ------------------------------------------------------------------
    # Config-group operations
    # ------------------------------------------------------------------

    def get_config_group(self, name: str = None):
        """Return a single config group dict (by name) or a list of all groups.

        GET /dataservice/v1/config-group?name=<name>
        """
        url = f'{self.base_url}/dataservice/v1/config-group'
        params = {'name': name} if name else {}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        groups = data if isinstance(data, list) else data.get('data', [])
        if name:
            for group in groups:
                if group.get('name') == name:
                    return group
            return None
        return groups

    def associate_device(self, config_group_id: str, device_id: str):
        """Associate a device to a config group.

        PUT /dataservice/v1/config-group/{configGroupId}/device/associate
        """
        url = f'{self.base_url}/dataservice/v1/config-group/{config_group_id}/device/associate'
        payload = {'deviceList': [device_id]}
        resp = self.session.put(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    def set_variables(self, config_group_id: str, device_id: str, variables: dict):
        """Push device variables to a config group.

        PUT /dataservice/v1/config-group/{configGroupId}/device/variables
        """
        url = f'{self.base_url}/dataservice/v1/config-group/{config_group_id}/device/variables'
        payload = {
            'solution': 'sdwan',
            'deviceVariables': [
                {'device-id': device_id, 'variables': variables},
            ],
        }
        resp = self.session.put(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    def deploy(self, config_group_id: str, device_id: str):
        """Trigger a config deployment for a device.

        POST /dataservice/v1/config-group/{configGroupId}/device/deploy
        """
        url = f'{self.base_url}/dataservice/v1/config-group/{config_group_id}/device/deploy'
        payload = {'deviceList': [device_id]}
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_bootstrap(self, device_id: str) -> str:
        """Fetch the cloud-init bootstrap configuration for a device.

        GET /dataservice/system/device/bootstrap/device/{deviceId}
            ?configtype=cloudinit&inclDefRootCert=true&version=v1
        """
        url = (
            f'{self.base_url}/dataservice/system/device/bootstrap/device/{device_id}'
            '?configtype=cloudinit&inclDefRootCert=true&version=v1'
        )
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get('bootstrapConfig', data)
