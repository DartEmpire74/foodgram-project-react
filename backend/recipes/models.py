from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

from recipes.constants import (
    CHAR_MAX_LENGTH, SLUG_MAX_LENGTH,)


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=CHAR_MAX_LENGTH)
    color = ColorField(
        verbose_name='Цвет',
        default='#FF0000')
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=SLUG_MAX_LENGTH,
        unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=CHAR_MAX_LENGTH)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=CHAR_MAX_LENGTH)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=CHAR_MAX_LENGTH)
    text = models.TextField(
        verbose_name='Описание рецепта')
    tags = models.ManyToManyField(
        Tag, through='TagRecipe', related_name='recipes',
        verbose_name='Теги')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredients_recipes')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients_recipes')
    amount = models.PositiveIntegerField()


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE)


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_lists')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_lists')

    class Meta:
        unique_together = ('user', 'recipe')


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites')
