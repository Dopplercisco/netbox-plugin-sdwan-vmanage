from extras.plugins import PluginConfig


class NetBoxSDWANConfig(PluginConfig):
    name = 'netbox_sdwan'
    verbose_name = 'NetBox SD-WAN vManage'
    description = 'Integrates NetBox with Cisco vManage SD-WAN'
    version = '0.1.0'
    author = 'Dopplercisco'
    base_url = 'sdwan'
    required_settings = ['vmanage_base_url', 'vmanage_username', 'vmanage_password']
    default_settings = {
        'device_cf_config_group': 'sdwan_config_group',
        'device_cf_rpserial': 'sdwan_rpserial',
        'allowed_role_slugs': ['sdwan-border-router', 'sdwan-edge-router'],
    }


config = NetBoxSDWANConfig
