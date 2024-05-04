from django.conf import settings
from django.db import migrations
from recipes.utils import random_color

def add_tags(apps, schema_editor):
    if not settings.ENABLE_TAG_MIGRATIONS:
        return
    Tag = apps.get_model('recipes', 'Tag')
    tags = [
        ('веганский', 'vegan', random_color()),
        ('безглютеновый', 'gluten_free', random_color()),
        ('низкокалорийный', 'low_calorie', random_color()),
    ]
    for name, slug, color in tags:
        Tag.objects.get_or_create(name=name, slug=slug, defaults={'color': color})

class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0002_add_ingredients'),
    ]
    operations = [
        migrations.RunPython(add_tags),
    ]
