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
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, null=True, blank=True)),
                ('description', models.CharField(max_length=200, null=True, blank=True)),
                ('category', models.CharField(blank=True, max_length=20, null=True, choices=[(b'Textbooks', b'Textbooks'), (b'Apparel', b'Apparel'), (b'Electronics', b'Electronics'), (b'Furniture', b'Furniture'), (b'Sublet', b'Sublet'), (b'Tutors', b'Tutors'), (b'Other', b'Other')])),
                ('price', models.CharField(max_length=100, null=True, blank=True)),
                ('order', models.IntegerField(default=0)),
                ('sold', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('image', models.ImageField(null=True, upload_to=b'products/', blank=True)),
                ('condition', models.CharField(blank=True, max_length=10, null=True, choices=[(b'New', b'New'), (b'Used', b'Used')])),
                ('owner', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-order'],
            },
        ),
    ]
