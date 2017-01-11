# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20160417_2224'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(default=0)),
                ('profile', models.ForeignKey(related_name='profile', to=settings.AUTH_USER_MODEL)),
                ('rater', models.ForeignKey(related_name='rater', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
