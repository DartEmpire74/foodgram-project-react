import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingList, Tag, TagRecipe
)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            is_subscribed = Subscription.objects.filter(user=current_user, following=obj).exists()
            return is_subscribed
        else:
            return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=True)
    ingredients = IngredientRecipeSerializer(many=True, write_only=True, required=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def validate(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError({"ingredients": "Это поле обязательно для обновления рецепта."})
        if 'tags' not in data:
            raise serializers.ValidationError({"tags": "Это поле обязательно для обновления рецепта."})
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                {"ingredients": ["Рецепт должен содержать хотя бы один ингредиент."]})
        seen = set()
        errors = []
        for ingredient in value:
            if ingredient['id'].id in seen:
                errors.append("Ингредиенты не должны повторяться.")
            seen.add(ingredient['id'].id)
            if ingredient['amount'] < 1:
                errors.append("Количество каждого ингредиента не должно быть < 1.")
        if errors:
            raise serializers.ValidationError({"ingredients": errors})
        return value

    def validate_tags(self, value):
        errors = []
        if not value:
            errors.append("Рецепт должен содержать хотя бы один тег.")
        if len(value) != len(set(value)):
            errors.append("Теги не должны повторяться.")
        if errors:
            raise serializers.ValidationError({"tags": errors})
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                {"cooking_time": ["Время приготовления не должно быть < 1 минуты."]})
        return value

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj).exists() if request and request.user.is_authenticated else False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return Favorite.objects.filter(
            user=request.user, recipe=obj).exists() if request and request.user.is_authenticated else False

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)

        for tag_data in tags_data:
            TagRecipe.objects.create(recipe=recipe, tag_id=tag_data.id)

        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'].id,
                amount=ingredient_data['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        instance.tags.clear()

        tags_data = validated_data.get('tags')
        for tag_data in tags_data:
            instance.tags.add(tag_data)

        IngredientRecipe.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.get('ingredients')
        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient_id=ingredient_data['id'].id,
                amount=ingredient_data['amount']
            )

        instance.save()

        return instance

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = obj.ingredients_recipes.all()
        return [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            } for ingredient in ingredients
        ]

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', "is_in_shopping_cart",
            "name", "image", "text", "cooking_time"
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='following.email', read_only=True)
    id = serializers.IntegerField(source='following.id', read_only=True)
    username = serializers.CharField(source='following.username', read_only=True)
    first_name = serializers.CharField(source='following.first_name', read_only=True)
    last_name = serializers.CharField(source='following.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='following.recipes.count', read_only=True)

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit', 10)
        limited_recipes = obj.following.recipes.all()[:int(limit)]
        return RecipeShortSerializer(limited_recipes, many=True).data

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        return Subscription.objects.filter(user=user, following=instance.following).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeShortSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['recipe']

    def to_representation(self, instance):
        recipe = instance.recipe
        serializer = RecipeShortSerializer(recipe)
        return serializer.data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe_id = self.context['request'].parser_context['kwargs']['pk']
        recipe = Recipe.objects.get(id=recipe_id)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError("Рецепт уже находится в избранном.", code=status.HTTP_400_BAD_REQUEST)
        favorite_recipe = Favorite.objects.create(user=user, recipe=recipe)

        return favorite_recipe
