from django.conf import settings
import csv
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations


def migrate_ingredients(apps, schema_editor):
    if not settings.ENABLE_INGREDIENT_MIGRATIONS:
        return
    Ingredient = apps.get_model('recipes', 'Ingredient')
    data_path = Path('ingredient_data')
    with open(data_path / 'ingredients.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            name, measurement_unit = row
            try:
                ingredient = Ingredient.objects.get(name=name)
            except ObjectDoesNotExist:
                ingredient = Ingredient.objects.create(name=name, measurement_unit=measurement_unit)


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0001_initial_squashed_0008_alter_ingredientrecipe_amount_and_more'),
    ]
    operations = [
        migrations.RunPython(migrate_ingredients),
    ]
