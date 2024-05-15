# Generated by Django 5.0.6 on 2024-05-15 13:07

import control.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0008_alter_groupdoorlock_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doorlock',
            name='comment',
            field=models.CharField(default='', max_length=200, verbose_name='简介'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='doorlock',
            name='key',
            field=models.CharField(max_length=200, validators=[control.models.validate_exact_length], verbose_name='密钥'),
        ),
        migrations.AlterField(
            model_name='doorlock',
            name='last_seen',
            field=models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), verbose_name='上次心跳'),
        ),
    ]