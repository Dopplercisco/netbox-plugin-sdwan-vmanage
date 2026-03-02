import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from dcim.models import Device

from .forms import SDWANMappingForm
from .models import SDWANMapping
from .sdwan_client import SDWANClient


def _get_sdwan_client() -> SDWANClient:
    """Build an authenticated SDWANClient from PLUGINS_CONFIG."""
    cfg = settings.PLUGINS_CONFIG.get('netbox_sdwan', {})
    client = SDWANClient(
        base_url=cfg.get('vmanage_base_url', ''),
        username=cfg.get('vmanage_username', ''),
        password=cfg.get('vmanage_password', ''),
    )
    client.login()
    return client


def _resolve_config_group(client: SDWANClient, config_group_name: str):
    """Return (config_group_id, error_message) for the named config group."""
    group = client.get_config_group(name=config_group_name)
    if not group:
        return None, f'Config group "{config_group_name}" not found in vManage.'
    group_id = group.get('id') or group.get('configGroupId')
    if not group_id:
        return None, f'Config group "{config_group_name}" has no id field.'
    return group_id, None


# ---------------------------------------------------------------------------
# Mapping create / edit
# ---------------------------------------------------------------------------

class SDWANMappingEditView(LoginRequiredMixin, View):
    """Create or update the SDWANMapping for a device, with optional
    backfill from the device's custom fields."""

    def _get_or_create_mapping(self, device: Device) -> SDWANMapping:
        try:
            return device.sdwan_mapping
        except SDWANMapping.DoesNotExist:
            mapping = SDWANMapping(device=device)
            mapping.backfill_from_custom_fields()
            return mapping

    def get(self, request, device_id: int):
        device = get_object_or_404(Device, pk=device_id)
        mapping = self._get_or_create_mapping(device)
        form = SDWANMappingForm(instance=mapping)
        return render(request, 'netbox_sdwan/sdwan_mapping_edit.html', {
            'device': device,
            'mapping': mapping,
            'form': form,
        })

    def post(self, request, device_id: int):
        device = get_object_or_404(Device, pk=device_id)
        mapping = self._get_or_create_mapping(device)
        form = SDWANMappingForm(request.POST, instance=mapping)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.device = device
            saved.save()
            form.save_m2m()
            messages.success(request, f'SD-WAN mapping saved for {device}.')
            return redirect('dcim:device', pk=device_id)
        return render(request, 'netbox_sdwan/sdwan_mapping_edit.html', {
            'device': device,
            'mapping': mapping,
            'form': form,
        })


# ---------------------------------------------------------------------------
# vManage actions
# ---------------------------------------------------------------------------

class AssociateConfigGroupView(LoginRequiredMixin, View):
    """Associate the device to its configured vManage config group."""

    def post(self, request, device_id: int):
        device = get_object_or_404(Device, pk=device_id)
        mapping = get_object_or_404(SDWANMapping, device=device)
        try:
            client = _get_sdwan_client()
            group_id, err = _resolve_config_group(client, mapping.config_group_name)
            if err:
                messages.error(request, err)
                return redirect('dcim:device', pk=device_id)
            client.associate_device(group_id, mapping.device_id)
            messages.success(
                request,
                f'Device {mapping.device_id} associated to config group '
                f'"{mapping.config_group_name}".',
            )
        except Exception as exc:
            messages.error(request, f'Association failed: {exc}')
        return redirect('dcim:device', pk=device_id)


class SetVariablesView(LoginRequiredMixin, View):
    """Push device variables (from rendered config JSON) to vManage."""

    def post(self, request, device_id: int):
        device = get_object_or_404(Device, pk=device_id)
        mapping = get_object_or_404(SDWANMapping, device=device)
        try:
            config_json = device.render_config()
            variables = json.loads(config_json)
            client = _get_sdwan_client()
            group_id, err = _resolve_config_group(client, mapping.config_group_name)
            if err:
                messages.error(request, err)
                return redirect('dcim:device', pk=device_id)
            client.set_variables(group_id, mapping.device_id, variables)
            messages.success(request, f'Variables set for device {mapping.device_id}.')
        except Exception as exc:
            messages.error(request, f'Set variables failed: {exc}')
        return redirect('dcim:device', pk=device_id)


class DeployConfigView(LoginRequiredMixin, View):
    """Trigger a config deployment in vManage."""

    def post(self, request, device_id: int):
        device = get_object_or_404(Device, pk=device_id)
        mapping = get_object_or_404(SDWANMapping, device=device)
        try:
            client = _get_sdwan_client()
            group_id, err = _resolve_config_group(client, mapping.config_group_name)
            if err:
                messages.error(request, err)
                return redirect('dcim:device', pk=device_id)
            client.deploy(group_id, mapping.device_id)
            messages.success(request, f'Deploy initiated for device {mapping.device_id}.')
        except Exception as exc:
            messages.error(request, f'Deploy failed: {exc}')
        return redirect('dcim:device', pk=device_id)


class BootstrapConfigView(LoginRequiredMixin, View):
    """Fetch the cloud-init bootstrap config from vManage and display it."""

    def get(self, request, device_id: int):
        device = get_object_or_404(Device, pk=device_id)
        mapping = get_object_or_404(SDWANMapping, device=device)
        bootstrap_config = None
        error = None
        try:
            client = _get_sdwan_client()
            bootstrap_config = client.get_bootstrap(mapping.device_id)
        except Exception as exc:
            error = str(exc)
        return render(request, 'netbox_sdwan/bootstrap.html', {
            'device': device,
            'mapping': mapping,
            'bootstrap_config': bootstrap_config,
            'error': error,
        })
