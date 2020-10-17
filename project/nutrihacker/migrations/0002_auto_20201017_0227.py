# Generated by Django 3.1.1 on 2020-10-17 06:27

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nutrihacker', '0001_initial'),
    ]

    operations = [
        # migrations.CreateModel(
            # name='Recipe',
            # fields=[
                # ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # ('name', models.CharField(default='Custom Recipe', max_length=50)),
                # ('in_progress', models.BooleanField(default=False)),
                # ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                # ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            # ],
        # ),
        migrations.AlterField(
            model_name='meallog',
            name='log_time',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(null=True),
        ),
        # migrations.CreateModel(
            # name='RecipeFood',
            # fields=[
                # ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # ('amount', models.IntegerField(default=1)),
                # ('amount_unit', models.CharField(default='g', max_length=50)),
                # ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrihacker.food')),
                # ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrihacker.recipe')),
            # ],
        # ),
    ]
