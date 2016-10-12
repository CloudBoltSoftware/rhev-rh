# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rhev', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rhevresourcehandler',
            name='networks',
            field=models.ManyToManyField(to='rhev.RhevNetwork', blank=True),
        ),
        migrations.AlterField(
            model_name='rhevresourcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='rhev.RhevOSBuildAttribute', blank=True),
        ),
    ]
