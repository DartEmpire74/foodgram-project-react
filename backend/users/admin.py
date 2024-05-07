from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from users.models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'recipe_count',
                    'followers_count',
                    )
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _recipe_count=Count('recipes'),
            _followers_count=Count('followers')
        )
        return queryset

    @admin.display(ordering='_recipe_count', description='Количество рецептов')
    def recipe_count(self, obj):
        return obj._recipe_count

    @admin.display(
        ordering='_followers_count', description='Количество подписчиков')
    def followers_count(self, obj):
        return obj._followers_count


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user__username',)
    list_filter = ('user',)
