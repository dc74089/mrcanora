# Generated by Django 3.1.14 on 2022-11-14 00:06

import classroom.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0010_student_bday'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('queuepos', models.IntegerField(default=classroom.models.get_next_queuepos)),
                ('prompt', models.TextField()),
                ('resolution', models.CharField(choices=[('1280x720', 'Landscape'), ('720x1280', 'Portrait'), ('1920x1080', 'Landscape HD'), ('1080x1920', 'Portrait HD'), ('1284x2778', 'iPhone 2k')], default='1280x720', max_length=50)),
                ('extra_params', models.TextField(blank=True, null=True)),
                ('state', models.IntegerField(choices=[(0, 'Submitted'), (2, 'Accepted'), (4, 'Enqueued'), (6, 'Processing'), (8, 'Awaiting Moderation'), (10, 'Fulfilled')], default=0)),
                ('submit_time', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, null=True, upload_to=classroom.models.user_dir)),
                ('approved', models.BooleanField(default=False)),
                ('finish_time', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.student')),
            ],
            options={
                'ordering': ['submit_time'],
            },
        ),
    ]