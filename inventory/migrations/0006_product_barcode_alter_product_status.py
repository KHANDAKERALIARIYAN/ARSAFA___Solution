# Generated by Django 4.2.23 on 2025-07-09 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_product_selling_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='barcode',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('low', 'Low'), ('fair', 'Fair')], default='good', max_length=10),
        ),
    ]
