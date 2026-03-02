import django.db.models.deletion
import taggit.managers

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # dcim.Device is required for the OneToOneField
        ('dcim', '0001_squashed_0135_auto_20200822_0915'),
        # extras.TaggedItem is the through-model for NetBoxModel's tags
        ('extras', '0001_squashed_0040_auto_20200604_1109'),
        # taggit Tag model
        ('taggit', '0005_auto_20220424_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='SDWANMapping',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=None),
                ),
                (
                    'config_group_name',
                    models.CharField(
                        blank=True,
                        help_text='Name of the vManage config group for this device.',
                        max_length=255,
                    ),
                ),
                (
                    'rp_serial',
                    models.CharField(
                        blank=True,
                        help_text='RP serial number used to compute the vManage device-id.',
                        max_length=255,
                    ),
                ),
                (
                    'device',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sdwan_mapping',
                        to='dcim.device',
                    ),
                ),
                (
                    'tags',
                    taggit.managers.TaggableManager(
                        help_text='A comma-separated list of tags.',
                        through='extras.TaggedItem',
                        to='taggit.Tag',
                        verbose_name='Tags',
                    ),
                ),
            ],
            options={
                'verbose_name': 'SD-WAN Mapping',
                'verbose_name_plural': 'SD-WAN Mappings',
            },
        ),
    ]
