# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-06 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0007_auto_20160803_1223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='owner',
            name='lock_inner_id',
        ),
        migrations.AddField(
            model_name='owner',
            name='lock_inner_id',
            field=models.ManyToManyField(to='portal.Lock'),
        ),
        migrations.AlterField(
            model_name='owner',
            name='owner',
            field=models.CharField(max_length=40),
        ),
    ]
