# Generated by Django 3.1.1 on 2020-10-26 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0016_auto_20201026_0959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='allergy',
        ),
        migrations.AddField(
            model_name='recipe',
            name='allergy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nutrihacker.allergy'),
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='diet',
        ),
        migrations.AddField(
            model_name='recipe',
            name='diet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nutrihacker.dietpreference'),
        ),
    ]