# Generated by Django 3.1.1 on 2020-12-16 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0037_auto_20201210_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='recipe_image',
            field=models.ImageField(blank=True, null='True', upload_to='Recipe_pic/'),
        ),
    ]
