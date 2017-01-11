# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_auto_20160528_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='university',
            name='latitude',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='university',
            name='longitude',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
