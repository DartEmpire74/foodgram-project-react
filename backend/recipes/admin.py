from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, Tag, TagRecipe, ShoppingList
)


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    extra = 1
    min_num = 1
    autocomplete_fields = ('tag',)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    min_num = 1
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

    @admin.display(description='Количество в избранном')
    def favorites_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')
    search_fields = ('tag__name', 'recipe__name')
    list_filter = ('tag', 'recipe')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    search_fields = ('ingredient__name', 'recipe__name')
    list_filter = ('ingredient', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
