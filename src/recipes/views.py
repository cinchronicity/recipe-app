from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Recipe, Favorite

# Create your views here.


# This view handles the homepage request.
# It receives the HTTP request and returns an HTML response.
def home(request):
    # Get featured recipes for homepage
    featured_recipes = Recipe.objects.all()[:6]  # Latest 6 recipes
    breakfast_recipes = Recipe.objects.filter(category="breakfast")[:3]
    dinner_recipes = Recipe.objects.filter(category="dinner")[:3]
    dessert_recipes = Recipe.objects.filter(category="dessert")[:3]

    context = {
        "featured_recipes": featured_recipes,
        "breakfast_recipes": breakfast_recipes,
        "dinner_recipes": dinner_recipes,
        "dessert_recipes": dessert_recipes,
    }
    return render(request, "recipes/recipes_home.html", context)


def recipes_list(request):
    # Get all recipes, ordered by creation date (newest first)
    recipes = Recipe.objects.all().order_by("-created_at")

    # Get recipe counts by category for sidebar/stats
    categories = Recipe.objects.values_list("category", flat=True).distinct()
    category_counts = {}
    for category in categories:
        category_counts[category] = Recipe.objects.filter(category=category).count()

    context = {
        "recipes": recipes,
        "total_recipes": recipes.count(),
        "category_counts": category_counts,
    }
    return render(request, "recipes/recipes_list.html", context)


def recipe_detail(request, id):
    # Get the specific recipe or return 404 if not found
    recipe = get_object_or_404(Recipe, id=id)

    # Get related recipes in same category for suggestions
    related_recipes = Recipe.objects.filter(category=recipe.category).exclude(id=id)[:3]

    # Check if user has favorited this recipe (if logged in)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, recipe=recipe).exists()

    context = {
        "recipe": recipe,
        "related_recipes": related_recipes,
        "is_favorite": is_favorite,
    }
    return render(request, "recipes/recipe_detail.html", context)


@login_required
def favorites_list(request):
    """Display user's favorite recipes (requires login)."""
    # Get all favorites for the current user
    user_favorites = Favorite.objects.filter(user=request.user).select_related("recipe")

    # Extract just the recipes for easier template handling
    favorite_recipes = [favorite.recipe for favorite in user_favorites]

    context = {
        "favorite_recipes": favorite_recipes,
        "total_favorites": len(favorite_recipes),
    }
    return render(request, "recipes/favorites_list.html", context)


@login_required
def add_favorite(request, recipe_id):
    """Add a recipe to user's favorites."""
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Create favorite if it doesn't exist
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)

    if created:
        messages.success(request, f'"{recipe.name}" has been added to your favorites!')
    else:
        messages.info(request, f'"{recipe.name}" is already in your favorites!')

    return redirect("recipes:recipe_detail", id=recipe_id)


@login_required
def remove_favorite(request, recipe_id):
    """Remove a recipe from user's favorites."""
    recipe = get_object_or_404(Recipe, id=recipe_id)

    try:
        favorite = Favorite.objects.get(user=request.user, recipe=recipe)
        favorite.delete()
        messages.success(
            request, f'"{recipe.name}" has been removed from your favorites!'
        )
    except Favorite.DoesNotExist:
        messages.error(request, f'"{recipe.name}" was not in your favorites!')

    # Redirect back to the referring page or favorites list
    return redirect(request.META.get("HTTP_REFERER", "recipes:favorites_list"))
