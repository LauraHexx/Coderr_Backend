# Generated by Django 5.2 on 2025-05-02 19:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='profile_pictures/')),
                ('location', models.CharField(max_length=255)),
                ('tel', models.CharField(max_length=20)),
                ('description', models.TextField(max_length=255)),
                ('working_hours', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('business', 'Business'), ('customer', 'Customer')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
