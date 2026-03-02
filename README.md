# netbox-plugin-sdwan-vmanage

A NetBox 3.5.7 plugin that integrates with **Cisco vManage SD-WAN**.

## Features

- **SDWANMapping model** — one-to-one mapping per NetBox Device, storing
  `config_group_name` and `rp_serial`; can be backfilled from Device custom
  fields (`sdwan_config_group` / `sdwan_rpserial`).
- **Device panel** — injects an SD-WAN card into the Device detail page
  showing config group, RP serial, and computed vManage device-id.
- **Actions available from the Device panel:**
  - **Associate** — associate the device to its vManage config group
  - **Set Variables** — push rendered-config JSON as device variables
  - **Deploy** — trigger a vManage config deployment
  - **Fetch Bootstrap** — display the cloud-init bootstrap config
- **vManage device-id computation:**
  `<DEVICE_TYPE_SLUG_UPPERCASED_WITHOUT_CISCO->-<rp_serial>`

---

## Installation (NetBox 3.5.7)

### 1. Install the package

```bash
pip install .
```

Or in development mode:

```bash
pip install -e .
```

### 2. Configure NetBox

Add to `configuration.py`:

```python
PLUGINS = ['netbox_sdwan']

PLUGINS_CONFIG = {
    'netbox_sdwan': {
        # Required
        'vmanage_base_url': 'https://vmanage.example.com',
        'vmanage_username': 'admin',
        'vmanage_password': 'secret',

        # Optional (match your Device custom field names)
        'device_cf_config_group': 'sdwan_config_group',   # default
        'device_cf_rpserial':     'sdwan_rpserial',        # default

        # Optional: restrict actions to devices with these role slugs
        'allowed_role_slugs': ['sdwan-border-router', 'sdwan-edge-router'],
    }
}
```

### 3. Run migrations

```bash
python manage.py migrate
```

> **Note:** If you encounter migration dependency errors, regenerate the
> initial migration inside your NetBox virtualenv:
> ```bash
> python manage.py makemigrations netbox_sdwan
> python manage.py migrate
> ```

### 4. Collect static files

```bash
python manage.py collectstatic --no-input
```

### 5. Restart services

```bash
sudo systemctl restart netbox netbox-rq
```

---

## Required Device Custom Fields

The plugin can backfill mapping data from two Device custom fields:

| Custom Field Slug    | Type   | Description                          |
|----------------------|--------|--------------------------------------|
| `sdwan_config_group` | String | vManage config group name            |
| `sdwan_rpserial`     | String | RP serial used for vManage device-id |

---

## Security Note

TLS verification is currently disabled (`verify=False`) for compatibility
with self-signed vManage certificates. To enable verification, set
`VERIFY_TLS = True` in `netbox_sdwan/sdwan_client.py` and provide a valid
CA bundle.

---

## CHANGELOG

### v0.1.0 (initial release)
- Initial plugin with SDWANMapping model, Device panel, and vManage
  Associate / Set Variables / Deploy / Fetch Bootstrap actions.