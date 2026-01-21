from django.db import models
from django.contrib.auth.models import User
from ingredients.models import Ingredient


class Recipe(models.Model):
    # --- Category choices (dropdown in admin) ---
    CATEGORY_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("entree", "Entree"),
        ("salad", "Salad"),
        ("soup", "Soup"),
        ("dessert", "Dessert"),
        ("snack", "Snack"),
        ("drink", "Drink"),
        ("other", "Other"),
    ]
    # --- Core fields ---
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
    )
    # --- Time + servings ---
    prep_time = models.PositiveIntegerField(default=0, help_text="Prep time in minutes")
    cooking_time = models.PositiveIntegerField(help_text="Cook time in minutes")
    servings = models.PositiveIntegerField(default=1)
    # --- Relationships ---
    ingredients = models.ManyToManyField(Ingredient, related_name="recipes")
    # --- Image upload (requires Pillow) ---
    # stored under MEDIA_ROOT/recipe_images/
    image = models.ImageField(
        upload_to="recipe_images/",
        blank=True,
        null=True,
        default="recipe_images/default-recipe.jpg",
    )
    # --- Timestamps (sorting + debugging) ---
    created_at = models.DateTimeField(auto_now_add=True)  # set once
    updated_at = models.DateTimeField(auto_now=True)  # updates on every save

    def __str__(self):
        return self.name

    # Calculated fields that update upon changes (not stored in DB)
    @property
    def total_time(self):
        return self.prep_time + self.cooking_time

    @property
    def difficulty(self):
        # (can tweak these thresholds anytime.)
        ingredient_count = self.ingredients.count()

        if self.total_time < 15 and ingredient_count <= 5:
            return "Easy"
        if self.total_time < 30 and ingredient_count <= 8:
            return "Medium"
        return "Hard"


class Favorite(models.Model):
    """Model to track user's favorite recipes."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe")  # Prevent duplicate favorites
        ordering = ["-created_at"]  # Show newest favorites first

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"
