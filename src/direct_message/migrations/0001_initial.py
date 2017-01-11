# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=150)),
                ('body', models.CharField(max_length=3000)),
                ('sent', models.DateTimeField(null=True, blank=True)),
                ('read_at', models.DateTimeField(null=True, blank=True)),
                ('read', models.BooleanField(default=False)),
                ('replied', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(related_name='parent_message', blank=True, to='direct_message.DirectMessage', null=True)),
                ('receiver', models.ForeignKey(related_name='received_direct_messages', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('sender', models.ForeignKey(related_name='sent_direct_messages', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
