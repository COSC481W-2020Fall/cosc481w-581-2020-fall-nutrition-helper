# Generated by Django 3.1.1 on 2020-12-04 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0026_recipe_foods'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profilePic',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]
