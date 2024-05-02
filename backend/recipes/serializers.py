from django.contrib.auth import get_user_model
from rest_framework import serializers, status

from recipes.constants import (
    MIN_INGREDIENT_AMOUNT, MIN_COOKING_TIME)
from recipes.fields import Base64ImageField
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingList, Tag)
from users.models import Subscription


User = get_user_model()


def add_ingredients_to_recipe(instance, ingredients_data):
    """Метод для формирования списка объектов IngredientRecipe."""
    ingredient_recipes = [
        IngredientRecipe(
            recipe=instance,
            ingredient=ingredient_data['id'],
            amount=ingredient_data['amount']
        )
        for ingredient_data in ingredients_data
    ]
    return ingredient_recipes


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return (current_user.is_authenticated and obj.followers.filter(
            user=current_user).exists())


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для записи IngredientRecipe."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения IngredientRecipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления Recipe."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)
    ingredients = IngredientRecipeSerializer(
        many=True, write_only=True, required=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags_display = TagSerializer(source='tags', many=True, read_only=True)
    ingredients_display = IngredientRecipeReadSerializer(
        source='ingredients_recipes', many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'tags_display',
            'ingredients_display', 'name', 'image', 'text', 'cooking_time'
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation['tags'] = representation.pop('tags_display', [])
        representation['ingredients'] = representation.pop(
            'ingredients_display', [])
        if request and request.user.is_authenticated:
            representation['is_in_shopping_cart'] = (
                instance.shopping_lists.filter(user=request.user).exists())
            representation['is_favorited'] = (
                instance.favorites.filter(user=request.user).exists())
        else:
            representation['is_in_shopping_cart'] = False
            representation['is_favorited'] = False
        return representation

    def validate(self, data):
        print("Validating data:", data)
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно "
                    "для обновления рецепта."})
        if 'tags' not in data:
            raise serializers.ValidationError(
                {"tags": "Это поле обязательно для обновления рецепта."})
        ingredients = [ingredient['id'] for ingredient in data['ingredients']]
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": [
                    "Рецепт должен содержать хотя бы один ингредиент."]})
        seen = set(ingredients)
        if len(seen) != len(ingredients):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться"})
        return data

    def validate_tags(self, value):
        errors = []
        if not value:
            errors.append(
                "Рецепт должен содержать хотя бы один тег.")
        if len(value) != len(set(value)):
            errors.append("Теги не должны повторяться.")
        if errors:
            raise serializers.ValidationError({"tags": errors})
        return value

    def validate_cooking_time(self, value):
        if value < MIN_COOKING_TIME:
            raise serializers.ValidationError(
                {"cooking_time":
                    [f"Время приготовления не должно "
                     f"быть < {MIN_COOKING_TIME} минуты."]})
        return value

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop(
            'ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        ingredient_recipes = add_ingredients_to_recipe(
            recipe, ingredients_data)
        IngredientRecipe.objects.bulk_create(ingredient_recipes)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get(
            'name', instance.name)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get(
            'image', instance.image)
        instance.tags.clear()
        tags_data = validated_data.get('tags')
        instance.tags.set(tags_data)
        IngredientRecipe.objects.filter(
            recipe=instance).delete()
        ingredients_data = validated_data.get('ingredients')
        ingredient_recipes = add_ingredients_to_recipe(
            instance, ingredients_data)
        IngredientRecipe.objects.bulk_create(ingredient_recipes)

        return instance


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения Recipe."""

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeReadSerializer(
        source='ingredients_recipes', many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            "name", "image", "text", "cooking_time"
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            representation['is_in_shopping_cart'] = (
                instance.shopping_lists.filter(user=request.user).exists())
            representation['is_favorited'] = (
                instance.favorites.filter(user=request.user).exists())
        else:
            representation['is_in_shopping_cart'] = False
            representation['is_favorited'] = False
        return representation


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о Recipe."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на пользователя."""

    class Meta:
        model = Subscription
        fields = ('following',)

    def validate(self, data):
        user = self.context['request'].user
        following = data['following']
        if user == following:
            raise serializers.ValidationError(
                "Вы не можете подписаться на себя.")
        if Subscription.objects.filter(
                user=user, following=following).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя.")
        return data

    def to_representation(self, instance):
        context = self.context
        context['request'].user = instance.user
        serializer = SubscriptionSerializer(
            instance.following, context=context)
        return serializer.data


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для просмотра подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (UserSerializer.Meta.fields + ('recipes', 'recipes_count'))

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit is not None:
            try:
                limit = int(limit)
                limited_recipes = obj.recipes.all()[:limit]
            except ValueError:
                raise serializers.ValidationError("Invalid limit value.")
        else:
            limited_recipes = obj.recipes.all()
        return RecipeShortSerializer(
            limited_recipes, many=True, context=self.context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в избранное"""

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe, context=self.context)
        return serializer.data

    def validate(self, data):
        try:
            user = data['user']
            recipe = data['recipe']

            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    "Рецепт уже находится в избранном.",
                    code=status.HTTP_400_BAD_REQUEST)

            return data
        except Exception as e:
            print("Error during update:", e)
            raise e


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = ('recipe',)

    def validate_recipe(self, value):
        user = self.context['request'].user
        if ShoppingList.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке покупок')
        return value

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context=self.context).data
