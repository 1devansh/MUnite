# Generated by Django 3.1 on 2020-09-01 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.CharField(default='Lorem ipsum', max_length=2000),
            preserve_default=False,
        ),
    ]
