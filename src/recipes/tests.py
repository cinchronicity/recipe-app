from django.test import TestCase

# Create your tests here.
from ingredients.models import Ingredient
from .models import Recipe

class RecipeModelTests(TestCase):
    def test_str_returns_name(self):
        recipe = Recipe.objects.create(
            name="Pasta",
            description="Simple pasta",
            cooking_time=15
        )
        self.assertEqual(str(recipe), "Pasta")

    def test_recipe_can_have_ingredients(self):
        salt = Ingredient.objects.create(name="Salt")
        garlic = Ingredient.objects.create(name="Garlic")

        recipe = Recipe.objects.create(
            name="Garlic Pasta",
            description="Quick dinner",
            cooking_time=20
        )
        recipe.ingredients.add(salt, garlic)

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertTrue(recipe.ingredients.filter(name="Salt").exists())