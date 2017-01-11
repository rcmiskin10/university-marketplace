# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('direct_message', '0004_remove_directmessage_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='Convo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('primary_user', models.ForeignKey(related_name='primary', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('secondary_user', models.ForeignKey(related_name='secondary', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
