# Generated by Django 4.0.5 on 2022-07-08 14:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0007_alter_user_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='old_orders',
            name='deliveryperson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_orders_user_deliveryperson', to=settings.AUTH_USER_MODEL),
        ),
    ]