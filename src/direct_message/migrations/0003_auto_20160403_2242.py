# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('direct_message', '0002_directmessage_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directmessage',
            name='sent',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
