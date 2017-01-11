# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20160523_0310'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='university',
            field=models.ForeignKey(blank=True, to='accounts.University', null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.date(2016, 5, 24)),
        ),
    ]
