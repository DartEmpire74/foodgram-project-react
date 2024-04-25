from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, Tag, TagRecipe,
)


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    extra = 1
    autocomplete_fields = ('tag',)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'favorites_count')
    inlines = (IngredientRecipeInLine, TagRecipeInLine)
    filter_horizontal = ('ingredients',)
    search_fields = ('name', 'text')
    list_filter = ('name', 'author', 'tags')

    def favorites_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()
    favorites_count.short_description = 'Количество в избранном'
