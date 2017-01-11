# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('direct_message', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='directmessage',
            name='timestamp',
            field=models.DateTimeField(default=None, auto_now_add=True),
            preserve_default=False,
        ),
    ]
