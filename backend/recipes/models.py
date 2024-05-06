from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (
    CHAR_MAX_LENGTH, SLUG_MAX_LENGTH, RETURN_STR_LENGTH,
    MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT)
from recipes.utils import random_color

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=CHAR_MAX_LENGTH)
    color = ColorField(
        verbose_name='Цвет',
        default=random_color,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=SLUG_MAX_LENGTH,
        unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:RETURN_STR_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=CHAR_MAX_LENGTH)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=CHAR_MAX_LENGTH)

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='measurament_unit_name_unique'
            ),
        )

    def __str__(self):
        return self.name[:RETURN_STR_LENGTH]


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
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_COOKING_TIME)])
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name[:RETURN_STR_LENGTH]


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE,
        related_name='ingredients_recipes')
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE,
        related_name='ingredients_recipes')
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)],
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = "ингредиент_рецепта"
        verbose_name_plural = 'Ингредиенты_рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='ingredient_recipe_unique'
            ),
        )

    def __str__(self):
        return (f'{self.ingredient.name} в "{self.recipe.name}" — '
                f'{self.amount}')[:RETURN_STR_LENGTH]


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, verbose_name='Тег', on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)

    class Meta:
        ordering = ('recipe',)
        verbose_name = "тег_рецепта"
        verbose_name_plural = 'Теги_рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('tag', 'recipe'),
                name='tag_recipe_unique'
            ),
        )

    def __str__(self):
        return (f'Тег "{self.tag.name}" для '
                f'"{self.recipe.name}"')[:RETURN_STR_LENGTH]


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE,
        related_name='shopping_lists')
    recipe = models.ForeignKey(
        Recipe, verbose_name="Рецепт", on_delete=models.CASCADE,
        related_name='shopping_lists')

    class Meta:
        ordering = ('recipe',)
        verbose_name = "список покупок"
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_recipe_in_list_unique'
            ),
        )

    def __str__(self):
        return (f'{self.user.username} — '
                f'"{self.recipe.name}"')[:RETURN_STR_LENGTH]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE,
        related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, verbose_name="Рецепт", on_delete=models.CASCADE,
        related_name='favorites')

    class Meta:
        ordering = ('recipe',)
        verbose_name = "избранное"
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_recipe_in_favorite_unique'
            ),
        )

    def __str__(self):
        return (f'{self.user.username} избранное: '
                f'"{self.recipe.name}"')[:RETURN_STR_LENGTH]
