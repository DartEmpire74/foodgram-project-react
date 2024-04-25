import csv

from django.contrib.auth import get_user_model
from django.db.models import Sum, F
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS, IsAuthenticated)
from rest_framework.response import Response

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingList, Tag
)
from recipes.pagination import StandardResultsSetPagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (
    FavoriteRecipeSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeShortSerializer,
    RecipeWriteSerializer, SubscriptionSerializer, TagSerializer)
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
    permission_classes = [IsAuthenticatedOrReadOnly,]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для работы с моделью рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        write_serializer = RecipeWriteSerializer(
            instance, data=request.data, context={'request': request},
            partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)
        read_serializer = RecipeReadSerializer(
            instance, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        write_serializer = RecipeWriteSerializer(
            data=request.data, context={'request': request})
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        read_serializer = RecipeReadSerializer(
            write_serializer.instance, context={'request': request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(
            read_serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except NotFound:
            return Response(
                {"detail": "Cтраница не найдена."},
                status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

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
                data={'recipe': recipe.id}, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
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
            _, created = ShoppingList.objects.get_or_create(
                user=user, recipe=recipe)
            if created:
                serializer = RecipeShortSerializer(
                    recipe, context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Этот рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
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
        shopping_items = IngredientRecipe.objects.filter(
            recipe__shopping_lists__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        filename = f'{user.username}_shopping_list.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'},
        )
        writer = csv.writer(response)
        writer.writerow(['Ingredient', 'Amount', 'Unit'])

        for item in shopping_items:
            writer.writerow(
                [item['ingredient__name'], item['total_amount'],
                 item['ingredient__measurement_unit']])

        return response


class SubscriptionViewSet(viewsets.GenericViewSet):
    """Viewset для работы с моделью подписок"""

    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        subscriptions = self.queryset.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, id=None):
        if request.user.id == int(id):
            return Response(
                {'error': 'Вы не можете подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST)
        following = get_object_or_404(User, id=id)
        subscription, created = Subscription.objects.get_or_create(
            user=request.user, following=following)
        if not created:
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionSerializer(
            subscription, context={'request': request})
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='subscribe')
    def unsubscribe(self, request, id=None):
        try:
            following = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND)
        try:
            subscription = Subscription.objects.get(
                user=request.user, following=following)
            subscription.delete()
            return Response(
                {'message': 'Вы успешно отписались.'},
                status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)
