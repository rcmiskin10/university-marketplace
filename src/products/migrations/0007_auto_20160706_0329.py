# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_service'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='name',
        ),
        migrations.RemoveField(
            model_name='service',
            name='user',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
    ]
