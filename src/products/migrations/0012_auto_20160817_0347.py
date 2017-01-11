# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_auto_20160817_0347'),
        ('products', '0011_auto_20160809_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='doservice',
            name='university',
            field=models.ForeignKey(blank=True, to='accounts.University', null=True),
        ),
        migrations.AddField(
            model_name='wantservice',
            name='university',
            field=models.ForeignKey(blank=True, to='accounts.University', null=True),
        ),
    ]
