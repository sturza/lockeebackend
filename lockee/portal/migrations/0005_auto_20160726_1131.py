# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 08:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_auto_20160725_1546'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lock',
            old_name='lock_name',
            new_name='lock_inner_id',
        ),
    ]
