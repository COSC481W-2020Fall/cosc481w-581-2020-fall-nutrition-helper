# Generated by Django 3.1.1 on 2020-12-06 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0027_profile_profilepic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profilePic',
            field=models.ImageField(default='default.jpg', upload_to='profile_picture'),
        ),
    ]
