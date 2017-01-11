# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20160417_2025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='count',
        ),
        migrations.RemoveField(
            model_name='myuser',
            name='rating',
        ),
    ]
