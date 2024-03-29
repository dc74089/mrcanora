# Generated by Django 3.1.14 on 2022-07-01 20:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0007_auto_20220519_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='musicsuggestion',
            name='added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='used_stars',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='student',
            name='canvas_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
