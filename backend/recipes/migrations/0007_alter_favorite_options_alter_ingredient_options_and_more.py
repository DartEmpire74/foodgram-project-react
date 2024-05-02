# Generated by Django 4.2 on 2024-04-27 17:33

import colorfield.fields
from django.db import migrations, models
import django.utils.timezone
import recipes.utils


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipe_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('recipe',), 'verbose_name': 'избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'ordering': ('recipe',), 'verbose_name': 'ингредиент_рецепта', 'verbose_name_plural': 'Ингредиенты_рецептов'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-created_at',), 'verbose_name': 'рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='shoppinglist',
            options={'ordering': ('recipe',), 'verbose_name': 'список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterModelOptions(
            name='tagrecipe',
            options={'ordering': ('recipe',), 'verbose_name': 'тег_рецепта', 'verbose_name_plural': 'Теги_рецептов'},
        ),
        migrations.AlterUniqueTogether(
            name='shoppinglist',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='recipe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default=recipes.utils.random_color, image_field=None, max_length=25, samples=None, unique=True, verbose_name='Цвет'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='user_recipe_in_favorite_unique'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='measurament_unit_name_unique'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='ingredient_recipe_unique'),
        ),
        migrations.AddConstraint(
            model_name='shoppinglist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='user_recipe_in_list_unique'),
        ),
        migrations.AddConstraint(
            model_name='tagrecipe',
            constraint=models.UniqueConstraint(fields=('tag', 'recipe'), name='tag_recipe_unique'),
        ),
    ]