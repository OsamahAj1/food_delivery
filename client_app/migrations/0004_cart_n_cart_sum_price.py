# Generated by Django 4.0.5 on 2022-07-04 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0003_user_is_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='n',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cart',
            name='sum_price',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=6),
            preserve_default=False,
        ),
    ]
