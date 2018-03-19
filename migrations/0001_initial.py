# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('resourcehandlers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RhevNetwork',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork')),
                ('uuid', models.CharField(default='', max_length=36)),
            ],
            options={
                'abstract': False,
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.CreateModel(
            name='RhevOSBuildAttribute',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute')),
                ('template_name', models.CharField(max_length=100)),
                ('uuid', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'RHEV OS Build Attribute',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='RhevResourceHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler')),
                ('clusterName', models.CharField(default='', max_length=100)),
                ('networks', models.ManyToManyField(to='rhev.RhevNetwork', null=True, blank=True)),
                ('os_build_attributes', models.ManyToManyField(to='rhev.RhevOSBuildAttribute', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
    ]
