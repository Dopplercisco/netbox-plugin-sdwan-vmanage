from django.db import models

from netbox.models import NetBoxModel
from dcim.models import Device


class SDWANMapping(NetBoxModel):
    """Per-device SD-WAN mapping that associates a NetBox Device with
    a vManage config group and stores the RP serial number used to
    compute the vManage device-id."""

    device = models.OneToOneField(
        to=Device,
        on_delete=models.CASCADE,
        related_name='sdwan_mapping',
    )
    config_group_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Name of the vManage config group for this device.',
    )
    rp_serial = models.CharField(
        max_length=255,
        blank=True,
        help_text='RP serial number used to compute the vManage device-id.',
    )

    class Meta:
        verbose_name = 'SD-WAN Mapping'
        verbose_name_plural = 'SD-WAN Mappings'

    def __str__(self):
        return f'SD-WAN Mapping: {self.device}'

    @property
    def device_id(self):
        """Compute the vManage device-id from the device type slug and RP serial.

        Logic mirrors the existing automation:
          model = device_type.slug.upper().replace('CISCO-', '')
          device_id = f'{model}-{rp_serial}'
        """
        if not self.rp_serial:
            return None
        model = self.device.device_type.slug.upper().replace('CISCO-', '')
        return f'{model}-{self.rp_serial}'

    def backfill_from_custom_fields(self):
        """Populate config_group_name / rp_serial from Device custom fields
        when the plugin custom-field names are configured."""
        from django.conf import settings

        plugin_cfg = settings.PLUGINS_CONFIG.get('netbox_sdwan', {})
        cf_config_group = plugin_cfg.get('device_cf_config_group', 'sdwan_config_group')
        cf_rpserial = plugin_cfg.get('device_cf_rpserial', 'sdwan_rpserial')

        cfs = self.device.custom_field_data or {}
        if not self.config_group_name and cfs.get(cf_config_group):
            self.config_group_name = cfs[cf_config_group]
        if not self.rp_serial and cfs.get(cf_rpserial):
            self.rp_serial = cfs[cf_rpserial]
