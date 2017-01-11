# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_auto_20160528_2145'),
    ]

    operations = [
        migrations.RenameField(
            model_name='university',
            old_name='country',
            new_name='state',
        ),
        migrations.RemoveField(
            model_name='university',
            name='web_page',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.date(2016, 5, 29)),
        ),
    ]
