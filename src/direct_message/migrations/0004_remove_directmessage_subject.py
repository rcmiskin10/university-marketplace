# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('direct_message', '0003_auto_20160403_2242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='directmessage',
            name='subject',
        ),
    ]
