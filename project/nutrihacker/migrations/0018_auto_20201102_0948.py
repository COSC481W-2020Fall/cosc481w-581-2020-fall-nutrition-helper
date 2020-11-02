# Generated by Django 3.1.1 on 2020-11-02 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nutrihacker', '0017_auto_20201026_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='allergy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nutrihacker.allergy'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='diet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nutrihacker.dietpreference'),
        ),
    ]
