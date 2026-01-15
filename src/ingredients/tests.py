from django.test import TestCase

# Create your tests here.
from .models import Ingredient

class IngredientModelTests(TestCase):
    def test_str_returns_name(self):
        ingredient = Ingredient.objects.create(name="Salt")
        self.assertEqual(str(ingredient), "Salt")

    def test_name_is_unique(self):
        Ingredient.objects.create(name="Garlic")
        with self.assertRaises(Exception):
            Ingredient.objects.create(name="Garlic")