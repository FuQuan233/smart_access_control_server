# Generated by Django 5.0.3 on 2024-04-03 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0003_rename_group_doorlock_groupdoorlock_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupdoorlock',
            name='doorlock',
        ),
        migrations.AddField(
            model_name='groupdoorlock',
            name='doorlock',
            field=models.ManyToManyField(to='control.doorlock'),
        ),
    ]