# Generated by Django 3.1.1 on 2020-12-10 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0035_auto_20201210_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='recipe_image',
            field=models.ImageField(blank='True', null='True', upload_to='Recipe_pic/'),
            preserve_default='True',
        ),
    ]