# Generated by Django 4.1.4 on 2022-12-29 05:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friendschat', '0010_friendrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='request_for',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests', to='friendschat.chatuser'),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='request_from',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='friendschat.chatuser'),
        ),
    ]
