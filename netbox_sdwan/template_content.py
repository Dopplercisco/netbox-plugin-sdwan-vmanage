from extras.plugins import PluginTemplateExtension

from .models import SDWANMapping


class DeviceSDWANContent(PluginTemplateExtension):
    """Inject an SD-WAN details panel into the right column of the Device
    detail page."""

    model = 'dcim.device'

    def right_page(self):
        device = self.context['object']
        try:
            mapping = device.sdwan_mapping
        except SDWANMapping.DoesNotExist:
            mapping = None
        return self.render(
            'netbox_sdwan/device_sdwan_panel.html',
            extra_context={'sdwan_mapping': mapping},
        )


template_extensions = [DeviceSDWANContent]
