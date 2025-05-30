# Generated by Django 5.2 on 2025-05-26 08:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0027_alter_customerreview_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='FooterContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('support_text', models.CharField(default='If you need support, just give us a call.', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ContactPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='dashboard.footercontact')),
            ],
        ),
        migrations.CreateModel(
            name='ContactEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='dashboard.footercontact')),
            ],
        ),
    ]
