# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-09 13:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metaphor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100)),
                ('word_type', models.CharField(max_length=50)),
                ('definition', models.CharField(max_length=1000)),
            ],
        ),
    ]
