# Generated by Django 5.0.4 on 2024-05-14 12:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_email'),
        ('requests', '0005_alter_favoriterecruiter_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoriterecruiter',
            name='recruiter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='accounts.recruiterprofile', verbose_name='Ulubiony rekruter'),
        ),
    ]