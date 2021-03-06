# Generated by Django 3.1.7 on 2021-04-06 18:30

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(blank=True, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='photographer',
            name='slug',
            field=models.SlugField(blank=True, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.ForeignKey(on_delete=models.SET(core.models.default_category), related_name='events', to='core.category'),
        ),
        migrations.AlterField(
            model_name='event',
            name='photographer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core.photographer'),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.BooleanField(default=True, help_text='Se attivo, questo evento è indicizzato.<br>Questa regola sovrasta anche la regola pubblico/privato', verbose_name='Stato'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='core.event'),
        ),
        migrations.AlterField(
            model_name='photographer',
            name='disk_space',
            field=models.PositiveIntegerField(default=500, help_text="Lo spazio, in MB, su disco dedicato all'upload di file zip quando ad esempio non si possiede un sito web dove caricare gli album", verbose_name='Spazio su disco'),
        ),
        migrations.AlterField(
            model_name='photographer',
            name='status',
            field=models.BooleanField(default=False, help_text='Se attivo, tutti gli eventi di questo fotografo sono visibili', verbose_name='Stato'),
        ),
        migrations.AlterField(
            model_name='photographer',
            name='telegram_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photographer', to='core.telegramuser'),
        ),
        migrations.AlterField(
            model_name='photomatch',
            name='photo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='core.photo'),
        ),
        migrations.AlterField(
            model_name='photomatch',
            name='telegram_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='core.telegramuser'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='url_encodings',
            field=models.FileField(blank=True, default=None, null=True, storage=core.models.OverwriteStorage(), upload_to=core.models.user_files, verbose_name='Encodings'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='url_video',
            field=models.FileField(blank=True, default=None, null=True, storage=core.models.OverwriteStorage(), upload_to=core.models.user_files, verbose_name='Video'),
        ),
    ]
