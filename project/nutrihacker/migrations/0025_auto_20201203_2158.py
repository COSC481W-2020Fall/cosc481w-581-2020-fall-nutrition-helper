# Generated by Django 3.1.1 on 2020-12-04 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0024_profile_caloriegoal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='caloriegoal',
            field=models.DecimalField(decimal_places=2, max_digits=7, null=True),
        ),
    ]
