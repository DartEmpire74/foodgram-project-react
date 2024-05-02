import csv

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS, IsAuthenticated)
from rest_framework.response import Response

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe,
    ShoppingList, Tag)
from recipes.pagination import StandardResultsSetPagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (
    FavoriteRecipeSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeWriteSerializer,
    SubscriptionSerializer, TagSerializer,
    UserSerializer, SubscribeSerializer,
    ShoppingListSerializer)
from users.models import Subscription


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для работы с моделью рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"detail": "Рецепт не найден."},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteRecipeSerializer(
                data={'recipe': recipe.id, 'user': user.id},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            recipe = get_object_or_404(Recipe, id=pk)
            try:
                favorite_recipe = Favorite.objects.get(
                    user=user, recipe=recipe)
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {"detail": "Рецепт не найден в избранном."},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            url_path='shopping_cart',
            permission_classes=[IsAuthenticated])
    def manage_shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"detail": "Рецепт не найден."},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingListSerializer(
                data={'recipe': recipe.id}, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)

        else:
            recipe = get_object_or_404(Recipe, id=pk)
            try:
                shopping_item = ShoppingList.objects.get(
                    user=user, recipe=recipe)
                shopping_item.delete()
                return Response(
                    {'status': 'Рецепт удален из списка покупок'},
                    status=status.HTTP_204_NO_CONTENT)
            except ShoppingList.DoesNotExist:
                return Response(
                    {'error': 'Рецепта не было в вашем списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_items = self.get_shopping_list_data(user)
        filename = f'{user.username}_shopping_list.csv'
        return self.prepare_and_send_csv(shopping_items, filename, user)

    def get_shopping_list_data(self, user):
        return IngredientRecipe.objects.filter(
            recipe__shopping_lists__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

    def prepare_and_send_csv(self, shopping_items, filename, user):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        writer = csv.writer(response)
        writer.writerow(['Ingredient', 'Amount', 'Unit'])
        for item in shopping_items:
            writer.writerow([item['ingredient__name'],
                             item['total_amount'],
                             item['ingredient__measurement_unit']])
        return response


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для работы с моделью пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def list_subscriptions(self, request):
        following_users = User.objects.filter(
            followers__user=request.user)
        page = self.paginate_queryset(following_users)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            following_users, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe_or_unsubscribe(self, request, pk=None):
        if request.method == 'POST':
            user = request.user
            following = get_object_or_404(User, id=pk)
            serializer = SubscribeSerializer(
                data={'following': following.id}, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            following = get_object_or_404(User, id=pk)
            try:
                subscription = Subscription.objects.get(
                    user=request.user, following_id=following.id)
            except Subscription.DoesNotExist:
                return Response(
                    {"detail": "Подписка не найдена."},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
