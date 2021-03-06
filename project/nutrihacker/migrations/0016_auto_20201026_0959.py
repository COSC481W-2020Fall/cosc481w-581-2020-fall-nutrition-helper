# Generated by Django 3.1.1 on 2020-10-26 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0015_auto_20201026_0930'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipefood',
            name='allergy',
        ),
        migrations.RemoveField(
            model_name='recipefood',
            name='diet',
        ),
        migrations.AddField(
            model_name='recipe',
            name='allergy',
            field=models.ManyToManyField(to='nutrihacker.Allergy'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='diet',
            field=models.ManyToManyField(to='nutrihacker.DietPreference'),
        ),
    ]
