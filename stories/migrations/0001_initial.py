# Generated by Django 3.2.6 on 2021-09-05 13:45

import ckeditor_uploader.fields
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20, null=True)),
                ('subject', models.CharField(max_length=264)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('author', models.CharField(max_length=250)),
                ('url', models.URLField(null=True)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField()),
                ('public_day', models.DateField(default=datetime.date.today)),
                ('image', models.ImageField(default='stories/images/default.jpg', upload_to='stories/images')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stories.category')),
            ],
        ),
    ]
