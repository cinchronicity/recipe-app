from django.shortcuts import render, get_object_or_404
from .models import Recipe

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

    context = {
        "recipe": recipe,
        "related_recipes": related_recipes,
    }
    return render(request, "recipes/recipe_detail.html", context)
