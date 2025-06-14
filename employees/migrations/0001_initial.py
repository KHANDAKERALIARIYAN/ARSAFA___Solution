# Generated by Django 4.2.23 on 2025-06-13 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('nid', models.CharField(max_length=20, unique=True)),
                ('designation', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=20)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('joining_date', models.DateField()),
            ],
        ),
    ]
