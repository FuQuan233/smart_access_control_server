# Generated by Django 5.0.3 on 2024-05-15 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0008_alter_groupdoorlock_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doorlock',
            name='last_seen',
            field=models.DateTimeField(default='1970-01-01 00:00:00', verbose_name='上次心跳'),
        ),
    ]
