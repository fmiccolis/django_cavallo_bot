# Generated by Django 3.1.7 on 2021-12-29 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20211229_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Username'),
        ),
    ]
