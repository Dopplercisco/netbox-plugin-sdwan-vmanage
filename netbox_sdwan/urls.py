from django.urls import path

from . import views

app_name = 'netbox_sdwan'

urlpatterns = [
    path(
        'device/<int:device_id>/edit/',
        views.SDWANMappingEditView.as_view(),
        name='mapping-edit',
    ),
    path(
        'device/<int:device_id>/associate/',
        views.AssociateConfigGroupView.as_view(),
        name='associate',
    ),
    path(
        'device/<int:device_id>/set-variables/',
        views.SetVariablesView.as_view(),
        name='set-variables',
    ),
    path(
        'device/<int:device_id>/deploy/',
        views.DeployConfigView.as_view(),
        name='deploy',
    ),
    path(
        'device/<int:device_id>/bootstrap/',
        views.BootstrapConfigView.as_view(),
        name='bootstrap',
    ),
]
