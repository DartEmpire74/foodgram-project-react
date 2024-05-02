from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from users.models import User


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

    def recipe_count(self, obj):
        return obj._recipe_count
    recipe_count.admin_order_field = '_recipe_count'
    recipe_count.short_description = 'Количество рецептов'

    def followers_count(self, obj):
        return obj._followers_count
    followers_count.admin_order_field = '_followers_count'
    followers_count.short_description = 'Количество подписчиков'
