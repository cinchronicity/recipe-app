from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ingredients.models import Ingredient
from .models import Recipe, Favorite


class RecipeModelTests(TestCase):
    """Test cases for Recipe model functionality and properties."""

    def setUp(self):
        """Set up test data for recipe model tests."""
        self.salt = Ingredient.objects.create(name="Salt")
        self.garlic = Ingredient.objects.create(name="Garlic")
        self.pasta = Ingredient.objects.create(name="Pasta")

    def test_str_returns_name(self):
        """Test that Recipe string representation returns recipe name."""
        recipe = Recipe.objects.create(
            name="Pasta", description="Simple pasta", cooking_time=15
        )
        self.assertEqual(str(recipe), "Pasta")

    def test_recipe_can_have_ingredients(self):
        """Test that recipes can be associated with multiple ingredients."""
        recipe = Recipe.objects.create(
            name="Garlic Pasta", description="Quick dinner", cooking_time=20
        )
        recipe.ingredients.add(self.salt, self.garlic)

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertTrue(recipe.ingredients.filter(name="Salt").exists())
        self.assertTrue(recipe.ingredients.filter(name="Garlic").exists())

    def test_recipe_total_time_calculation(self):
        """Test that total_time property correctly sums prep and cook time."""
        recipe = Recipe.objects.create(
            name="Complex Dish",
            description="Takes time to prepare",
            prep_time=30,
            cooking_time=45,
        )
        self.assertEqual(recipe.total_time, 75)

    def test_recipe_difficulty_easy(self):
        """Test that recipes with short time and few ingredients are marked as Easy."""
        recipe = Recipe.objects.create(
            name="Quick Snack",
            description="Fast and simple",
            prep_time=5,
            cooking_time=8,  # Total: 13 mins (< 15)
        )
        # Add few ingredients (≤5)
        recipe.ingredients.add(self.salt, self.garlic)

        self.assertEqual(recipe.difficulty, "Easy")

    def test_recipe_difficulty_medium(self):
        """Test that recipes with moderate time and ingredients are marked as Medium."""
        recipe = Recipe.objects.create(
            name="Standard Meal",
            description="Regular cooking time",
            prep_time=10,
            cooking_time=15,  # Total: 25 mins (< 30)
        )
        # Add moderate ingredients (≤8)
        recipe.ingredients.add(self.salt, self.garlic, self.pasta)

        self.assertEqual(recipe.difficulty, "Medium")

    def test_recipe_difficulty_hard(self):
        """Test that recipes with long time or many ingredients are marked as Hard."""
        recipe = Recipe.objects.create(
            name="Complex Meal",
            description="Long cooking process",
            prep_time=30,
            cooking_time=60,
        )
        # Total time (90) > 30 minutes should be Hard
        self.assertEqual(recipe.difficulty, "Hard")

    def test_recipe_category_choices(self):
        """Test that recipe categories can be set and retrieved correctly."""
        recipe = Recipe.objects.create(
            name="Breakfast Dish",
            description="Morning meal",
            category="breakfast",
            cooking_time=10,
        )
        self.assertEqual(recipe.category, "breakfast")
        self.assertEqual(recipe.get_category_display(), "Breakfast")

    def test_recipe_default_values(self):
        """Test that recipe model uses correct default values."""
        recipe = Recipe.objects.create(name="Minimal Recipe", cooking_time=5)
        self.assertEqual(recipe.prep_time, 0)
        self.assertEqual(recipe.servings, 1)
        self.assertEqual(recipe.category, "other")
        self.assertEqual(recipe.description, "")


class RecipeViewTests(TestCase):
    """Test cases for Recipe views and URL routing."""

    def setUp(self):
        """Set up test data and client for view tests."""
        self.client = Client()

        # Create test ingredients
        self.salt = Ingredient.objects.create(name="Salt")
        self.pepper = Ingredient.objects.create(name="Pepper")

        # Create test recipes for different categories
        self.breakfast_recipe = Recipe.objects.create(
            name="Scrambled Eggs",
            description="Quick breakfast",
            category="breakfast",
            prep_time=5,
            cooking_time=10,
        )
        self.breakfast_recipe.ingredients.add(self.salt)

        self.dinner_recipe = Recipe.objects.create(
            name="Grilled Chicken",
            description="Healthy dinner",
            category="dinner",
            prep_time=15,
            cooking_time=25,
        )
        self.dinner_recipe.ingredients.add(self.salt, self.pepper)

        self.dessert_recipe = Recipe.objects.create(
            name="Chocolate Cake",
            description="Sweet dessert",
            category="dessert",
            prep_time=45,
            cooking_time=60,
        )

    def test_home_view_status_code(self):
        """Test that home page loads successfully."""
        response = self.client.get(reverse("recipes:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_view_contains_featured_recipes(self):
        """Test that home page displays featured recipes."""
        response = self.client.get(reverse("recipes:home"))
        self.assertContains(response, "Scrambled Eggs")
        self.assertContains(response, "Grilled Chicken")
        self.assertContains(response, "Chocolate Cake")

    def test_home_view_category_sections(self):
        """Test that home page displays recipes by category."""
        response = self.client.get(reverse("recipes:home"))
        # Check context variables instead of template content
        self.assertIn("breakfast_recipes", response.context)
        self.assertIn("dinner_recipes", response.context)
        self.assertIn("dessert_recipes", response.context)

    def test_recipes_list_view_status_code(self):
        """Test that recipes list page loads successfully."""
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertEqual(response.status_code, 200)

    def test_recipes_list_view_shows_all_recipes(self):
        """Test that recipes list page displays all recipes."""
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertContains(response, "Scrambled Eggs")
        self.assertContains(response, "Grilled Chicken")
        self.assertContains(response, "Chocolate Cake")

    def test_recipes_list_view_shows_recipe_count(self):
        """Test that recipes list page shows correct recipe count."""
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertContains(response, "3 recipes found")  # Should show total count

    def test_recipes_list_view_shows_category_counts(self):
        """Test that recipes list page shows category breakdown."""
        response = self.client.get(reverse("recipes:recipes_list"))
        # Check that category counts are available in context
        self.assertEqual(response.context["category_counts"]["breakfast"], 1)
        self.assertEqual(response.context["category_counts"]["dinner"], 1)
        self.assertEqual(response.context["category_counts"]["dessert"], 1)

    def test_recipe_detail_view_status_code(self):
        """Test that recipe detail page loads successfully."""
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.breakfast_recipe.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_view_shows_recipe_info(self):
        """Test that recipe detail page displays all recipe information."""
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.breakfast_recipe.id])
        )
        self.assertContains(response, "Scrambled Eggs")
        self.assertContains(response, "Quick breakfast")
        self.assertContains(response, "5 min")  # prep time
        self.assertContains(response, "10 min")  # cooking time
        # Check that difficulty is displayed (actual value depends on calculation)
        self.assertContains(response, self.breakfast_recipe.difficulty)

    def test_recipe_detail_view_shows_ingredients(self):
        """Test that recipe detail page displays ingredient list."""
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.dinner_recipe.id])
        )
        self.assertContains(response, "Salt")
        self.assertContains(response, "Pepper")

    def test_recipe_detail_view_shows_related_recipes(self):
        """Test that recipe detail page shows related recipes from same category."""
        # Create another breakfast recipe
        another_breakfast = Recipe.objects.create(
            name="Pancakes",
            description="Fluffy pancakes",
            category="breakfast",
            cooking_time=15,
        )

        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.breakfast_recipe.id])
        )
        # Should show the other breakfast recipe as related
        self.assertContains(response, "Pancakes")

    def test_recipe_detail_view_404_for_nonexistent_recipe(self):
        """Test that recipe detail page returns 404 for non-existent recipe."""
        response = self.client.get(reverse("recipes:recipe_detail", args=[99999]))
        self.assertEqual(response.status_code, 404)


class RecipeURLTests(TestCase):
    """Test cases for Recipe URL patterns and routing."""

    def setUp(self):
        """Set up test data for URL tests."""
        self.recipe = Recipe.objects.create(
            name="Test Recipe", description="Test description", cooking_time=20
        )

    def test_home_url_resolves(self):
        """Test that home URL resolves correctly."""
        url = reverse("recipes:home")
        self.assertEqual(url, "/")

    def test_recipes_list_url_resolves(self):
        """Test that recipes list URL resolves correctly."""
        url = reverse("recipes:recipes_list")
        self.assertEqual(url, "/recipes/")

    def test_recipe_detail_url_resolves(self):
        """Test that recipe detail URL resolves correctly with recipe ID."""
        url = reverse("recipes:recipe_detail", args=[self.recipe.id])
        self.assertEqual(url, f"/recipes/{self.recipe.id}/")


class RecipeTemplateTests(TestCase):
    """Test cases for Recipe templates and template content."""

    def setUp(self):
        """Set up test data for template tests."""
        self.client = Client()

        self.recipe = Recipe.objects.create(
            name="Template Test Recipe",
            description="Testing template rendering",
            category="lunch",
            prep_time=10,
            cooking_time=20,
            servings=4,
        )

        self.ingredient = Ingredient.objects.create(name="Test Ingredient")
        self.recipe.ingredients.add(self.ingredient)

    def test_home_template_uses_correct_template(self):
        """Test that home view uses the correct template."""
        response = self.client.get(reverse("recipes:home"))
        self.assertTemplateUsed(response, "recipes/recipes_home.html")

    def test_recipes_list_template_uses_correct_template(self):
        """Test that recipes list view uses the correct template."""
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertTemplateUsed(response, "recipes/recipes_list.html")

    def test_recipe_detail_template_uses_correct_template(self):
        """Test that recipe detail view uses the correct template."""
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.id])
        )
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")

    def test_recipe_links_in_templates_work(self):
        """Test that recipe links in templates generate correct URLs."""
        expected_detail_url = reverse("recipes:recipe_detail", args=[self.recipe.id])

        # Test recipes list page recipe links (where individual recipe links exist)
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertContains(response, expected_detail_url)

    def test_navigation_links_work(self):
        """Test that navigation links in templates work correctly."""
        # Test navigation links from home page
        response = self.client.get(reverse("recipes:home"))
        self.assertContains(response, reverse("recipes:home"))
        self.assertContains(response, reverse("recipes:recipes_list"))

        # Test navigation links from recipes list
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertContains(response, reverse("recipes:home"))

        # Test navigation links from recipe detail
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.id])
        )
        self.assertContains(response, reverse("recipes:home"))
        self.assertContains(response, reverse("recipes:recipes_list"))

    def test_recipe_detail_back_link_works(self):
        """Test that back to recipes link in recipe detail works."""
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.id])
        )
        self.assertContains(response, reverse("recipes:recipes_list"))
        self.assertContains(response, "Back to Recipes")


class RecipeIntegrationTests(TestCase):
    """Integration tests for complete recipe functionality."""

    def setUp(self):
        """Set up comprehensive test data for integration tests."""
        self.client = Client()

        # Create ingredients
        self.ingredients = []
        ingredient_names = [
            "Flour",
            "Eggs",
            "Milk",
            "Sugar",
            "Butter",
            "Salt",
            "Pepper",
            "Garlic",
            "Onion",
        ]
        for name in ingredient_names:
            ingredient = Ingredient.objects.create(name=name)
            self.ingredients.append(ingredient)

        # Create recipes with different characteristics
        self.easy_recipe = Recipe.objects.create(
            name="Simple Toast",
            description="Quick breakfast toast",
            category="breakfast",
            prep_time=2,
            cooking_time=3,
            servings=1,
        )
        self.easy_recipe.ingredients.add(
            self.ingredients[0], self.ingredients[5]
        )  # Flour, Salt

        self.medium_recipe = Recipe.objects.create(
            name="Scrambled Eggs",
            description="Classic breakfast eggs",
            category="breakfast",
            prep_time=5,
            cooking_time=10,
            servings=2,
        )
        self.medium_recipe.ingredients.add(
            self.ingredients[1], self.ingredients[4], self.ingredients[5]
        )  # Eggs, Butter, Salt

        self.hard_recipe = Recipe.objects.create(
            name="Complex Pasta",
            description="Multi-step pasta dish",
            category="dinner",
            prep_time=30,
            cooking_time=45,
            servings=6,
        )
        # Add many ingredients to make it hard
        for ingredient in self.ingredients[:8]:
            self.hard_recipe.ingredients.add(ingredient)

    def test_complete_user_journey(self):
        """Test a complete user journey through the application."""
        # 1. User visits home page
        response = self.client.get(reverse("recipes:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Simple Toast")

        # 2. User navigates to recipes list
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "3 recipes found")

        # 3. User clicks on a recipe to view details
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.medium_recipe.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scrambled Eggs")
        self.assertContains(response, "Classic breakfast eggs")
        self.assertContains(response, "Medium")  # Check difficulty calculation

        # 4. User navigates back to recipes list
        response = self.client.get(reverse("recipes:recipes_list"))
        self.assertEqual(response.status_code, 200)

    def test_difficulty_calculations_across_recipes(self):
        """Test that difficulty calculations work correctly for all recipe types."""
        self.assertEqual(self.easy_recipe.difficulty, "Easy")
        self.assertEqual(self.medium_recipe.difficulty, "Medium")
        self.assertEqual(self.hard_recipe.difficulty, "Hard")

    def test_category_filtering_data_integrity(self):
        """Test that category counts and filtering data is accurate."""
        response = self.client.get(reverse("recipes:recipes_list"))

        # Check category counts
        category_counts = response.context["category_counts"]
        self.assertEqual(
            category_counts["breakfast"], 2
        )  # Simple Toast + Scrambled Eggs
        self.assertEqual(category_counts["dinner"], 1)  # Complex Pasta

        # Check total count
        self.assertEqual(response.context["total_recipes"], 3)


class FavoriteModelTests(TestCase):
    """Test cases for the Favorite model functionality."""

    def setUp(self):
        """Set up test data for favorite tests."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # Create a test recipe
        self.recipe = Recipe.objects.create(
            name="Test Recipe", description="A recipe for testing", cooking_time=20
        )

    def test_favorite_creation(self):
        """Test that a user can favorite a recipe successfully."""
        favorite = Favorite.objects.create(user=self.user, recipe=self.recipe)

        # Check the favorite was created
        self.assertEqual(Favorite.objects.count(), 1)
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.recipe, self.recipe)

    def test_favorite_string_representation(self):
        """Test that favorite displays nicely as 'username - recipe name'."""
        favorite = Favorite.objects.create(user=self.user, recipe=self.recipe)
        expected_string = f"{self.user.username} - {self.recipe.name}"
        self.assertEqual(str(favorite), expected_string)

    def test_unique_favorite_constraint(self):
        """Test that a user cannot favorite the same recipe twice."""
        # Create first favorite
        Favorite.objects.create(user=self.user, recipe=self.recipe)

        # Try to create duplicate favorite - should raise an error
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Favorite.objects.create(user=self.user, recipe=self.recipe)

    def test_user_can_favorite_multiple_recipes(self):
        """Test that one user can favorite many different recipes."""
        recipe2 = Recipe.objects.create(
            name="Another Recipe", description="Different recipe", cooking_time=15
        )

        # User favorites both recipes
        Favorite.objects.create(user=self.user, recipe=self.recipe)
        Favorite.objects.create(user=self.user, recipe=recipe2)

        # Check both favorites exist
        self.assertEqual(Favorite.objects.filter(user=self.user).count(), 2)

    def test_recipe_can_be_favorited_by_multiple_users(self):
        """Test that one recipe can be favorited by many different users."""
        user2 = User.objects.create_user(username="testuser2", password="testpass123")

        # Both users favorite the same recipe
        Favorite.objects.create(user=self.user, recipe=self.recipe)
        Favorite.objects.create(user=user2, recipe=self.recipe)

        # Check both favorites exist
        self.assertEqual(Favorite.objects.filter(recipe=self.recipe).count(), 2)


class FavoriteViewTests(TestCase):
    """Test cases for favorite-related views and user interactions."""

    def setUp(self):
        """Set up test data for favorite view tests."""
        # Create test user and log them in
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = Client()

        # Create test recipes
        self.recipe1 = Recipe.objects.create(
            name="Favorite Recipe 1", description="First test recipe", cooking_time=20
        )
        self.recipe2 = Recipe.objects.create(
            name="Favorite Recipe 2", description="Second test recipe", cooking_time=25
        )

    def test_favorites_list_requires_login(self):
        """Test that favorites page redirects anonymous users to login."""
        response = self.client.get(reverse("recipes:favorites_list"))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_favorites_list_shows_user_favorites(self):
        """Test that logged-in users see their favorited recipes."""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # Add a favorite recipe
        Favorite.objects.create(user=self.user, recipe=self.recipe1)

        # Visit favorites page
        response = self.client.get(reverse("recipes:favorites_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Favorite Recipe 1")
        self.assertContains(response, "Favorite Recipe")  # Check count display

    def test_empty_favorites_list_shows_helpful_message(self):
        """Test that users with no favorites see a helpful empty state."""
        # Log in user with no favorites
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("recipes:favorites_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No favorites yet!")
        self.assertContains(response, "Browse Recipes")  # Link to add favorites

    def test_add_favorite_requires_login(self):
        """Test that adding favorites requires user to be logged in."""
        response = self.client.get(
            reverse("recipes:add_favorite", args=[self.recipe1.id])
        )
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_add_favorite_creates_favorite_and_redirects(self):
        """Test that logged-in users can successfully add favorites."""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # Add favorite
        response = self.client.get(
            reverse("recipes:add_favorite", args=[self.recipe1.id])
        )

        # Should redirect back to recipe detail page
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/recipes/{self.recipe1.id}/", response.url)

        # Check favorite was created
        self.assertTrue(
            Favorite.objects.filter(user=self.user, recipe=self.recipe1).exists()
        )

    def test_add_favorite_twice_shows_friendly_message(self):
        """Test that trying to favorite same recipe twice shows helpful message."""
        # Log in and create existing favorite
        self.client.login(username="testuser", password="testpass123")
        Favorite.objects.create(user=self.user, recipe=self.recipe1)

        # Try to favorite again
        response = self.client.get(
            reverse("recipes:add_favorite", args=[self.recipe1.id])
        )

        # Should still work but show different message
        self.assertEqual(response.status_code, 302)
        # Only one favorite should exist
        self.assertEqual(
            Favorite.objects.filter(user=self.user, recipe=self.recipe1).count(), 1
        )

    def test_remove_favorite_requires_login(self):
        """Test that removing favorites requires user to be logged in."""
        response = self.client.get(
            reverse("recipes:remove_favorite", args=[self.recipe1.id])
        )
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_remove_favorite_deletes_favorite(self):
        """Test that logged-in users can successfully remove favorites."""
        # Log in and create favorite
        self.client.login(username="testuser", password="testpass123")
        Favorite.objects.create(user=self.user, recipe=self.recipe1)

        # Remove favorite
        response = self.client.get(
            reverse("recipes:remove_favorite", args=[self.recipe1.id])
        )

        # Should redirect (to referring page or favorites list)
        self.assertEqual(response.status_code, 302)

        # Check favorite was removed
        self.assertFalse(
            Favorite.objects.filter(user=self.user, recipe=self.recipe1).exists()
        )

    def test_recipe_detail_shows_favorite_status(self):
        """Test that recipe detail pages show correct favorite button for logged-in users."""
        # Log in user
        self.client.login(username="testuser", password="testpass123")

        # Visit recipe without favorite
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_favorite"])
        self.assertContains(response, "Add to Favorites")

        # Add favorite and visit again
        Favorite.objects.create(user=self.user, recipe=self.recipe1)
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_favorite"])
        self.assertContains(response, "Remove from Favorites")

    def test_anonymous_user_recipe_detail_has_no_favorite_buttons(self):
        """Test that non-logged-in users don't see favorite buttons on recipe pages."""
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe1.id])
        )
        self.assertEqual(response.status_code, 200)

        # Should not see favorite buttons
        self.assertNotContains(response, "Add to Favorites")
        self.assertNotContains(response, "Remove from Favorites")


class FavoriteURLTests(TestCase):
    """Test cases for favorite-related URL patterns."""

    def setUp(self):
        """Set up test data for URL tests."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.recipe = Recipe.objects.create(
            name="URL Test Recipe",
            description="Recipe for testing URLs",
            cooking_time=15,
        )

    def test_favorites_list_url_resolves(self):
        """Test that the favorites list URL works correctly."""
        url = reverse("recipes:favorites_list")
        self.assertEqual(url, "/favorites/")

    def test_add_favorite_url_resolves(self):
        """Test that the add favorite URL includes recipe ID correctly."""
        url = reverse("recipes:add_favorite", args=[self.recipe.id])
        self.assertEqual(url, f"/favorites/add/{self.recipe.id}/")

    def test_remove_favorite_url_resolves(self):
        """Test that the remove favorite URL includes recipe ID correctly."""
        url = reverse("recipes:remove_favorite", args=[self.recipe.id])
        self.assertEqual(url, f"/favorites/remove/{self.recipe.id}/")
