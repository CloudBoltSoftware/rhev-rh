# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-03 00:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rhev', '0002_auto_20161004_2121'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rhevresourcehandler',
            old_name='os_build_attributes',
            new_name='old_os_build_attributes',
        ),
    ]
