# Generated by Django 3.1.1 on 2020-10-21 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0010_auto_20201021_1333'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipefood',
            old_name='amount_unit',
            new_name='portions_unit',
        ),
    ]
