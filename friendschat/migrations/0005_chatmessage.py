# Generated by Django 4.1.4 on 2022-12-26 22:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friendschat', '0004_chatuser_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_message', models.TextField()),
                ('send_time', models.DateTimeField()),
                ('send_file', models.FileField(blank=True, default=None, null=True, upload_to='')),
                ('file_type', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('send_from', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='message_sent', to='friendschat.chatuser')),
                ('send_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='message_to', to='friendschat.chatuser')),
            ],
        ),
    ]
