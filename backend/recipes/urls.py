from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import (
    IngredientViewSet, RecipeViewSet,
    SubscriptionViewSet, TagViewSet)


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'users/subscriptions', SubscriptionViewSet, basename='subscriptions')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view({
        'post': 'subscribe',
        'delete': 'unsubscribe'
    }), name='subscribe'),
]
