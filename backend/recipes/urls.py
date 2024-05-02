from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import (
    IngredientViewSet, RecipeViewSet, TagViewSet,
    UserViewSet,)


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('users/subscriptions/', UserViewSet.as_view({
        'get': 'list_subscriptions'}), name='user-subscriptions'),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
