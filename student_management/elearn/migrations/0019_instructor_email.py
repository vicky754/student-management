# Generated by Django 3.2.9 on 2021-12-22 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0018_auto_20210507_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructor',
            name='email',
            field=models.CharField(default=True, max_length=255),
        ),
    ]