# Generated by Django 3.1.1 on 2020-12-10 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0029_auto_20201208_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profilePic',
            field=models.ImageField(blank=True, null=True, upload_to='profile_picture/'),
        ),
    ]
