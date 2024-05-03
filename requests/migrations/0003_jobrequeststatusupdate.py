# Generated by Django 5.0.4 on 2024-05-03 20:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0002_jobrequest_recruiter'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobRequestStatusUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_status', models.CharField(choices=[('pending', 'Oczekujące'), ('processing', 'W trakcie realizacji'), ('completed', 'Zakończone')], max_length=20)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('job_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_updates', to='requests.jobrequest')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]