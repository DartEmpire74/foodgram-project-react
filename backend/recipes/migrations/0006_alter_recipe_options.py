# Generated by Django 4.2 on 2024-04-25 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_ingredientrecipe_ingredient_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-id'], 'verbose_name': 'рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]