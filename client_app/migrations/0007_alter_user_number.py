# Generated by Django 4.0.5 on 2022-07-05 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0006_user_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='number',
            field=models.TextField(blank=True, default=1),
            preserve_default=False,
        ),
    ]
