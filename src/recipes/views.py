from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import pandas as pd
from .models import Recipe, Favorite
from .forms import RecipeSearchForm
from .chart_utils import generate_all_saved_recipe_charts

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
    """Display user's saved recipes with personal cooking insights charts."""
    # Get all favorites for the current user
    user_favorites = Favorite.objects.filter(user=request.user).select_related("recipe")

    # Extract just the recipes for easier template handling
    favorite_recipes = [favorite.recipe for favorite in user_favorites]

    # Generate charts for personal insights
    charts = generate_all_saved_recipe_charts(request.user)

    context = {
        "favorite_recipes": favorite_recipes,
        "total_favorites": len(favorite_recipes),
        "charts": charts,
        "has_charts": any(chart is not None for chart in charts.values()),
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


def recipe_search(request):
    """Search recipes with multiple criteria and display results as a table."""
    form = RecipeSearchForm(request.GET or None)
    search_results_df = None
    search_performed = False
    results_count = 0

    # Handle "Show All" functionality first (prioritize over search form)
    if "show_all" in request.GET:
        search_performed = True
        recipes_queryset = Recipe.objects.all().order_by("name")
        results_count = recipes_queryset.count()

        if results_count > 0:
            recipe_data = []
            for recipe in recipes_queryset:
                recipe_data.append(
                    {
                        "id": recipe.id,
                        "name": recipe.name,
                        "category": recipe.get_category_display(),
                        "difficulty": recipe.difficulty,
                        "prep_time": recipe.prep_time,
                        "cooking_time": recipe.cooking_time,
                        "total_time": recipe.total_time,
                        "servings": recipe.servings,
                        "description": (
                            recipe.description[:100] + "..."
                            if len(recipe.description) > 100
                            else recipe.description
                        ),
                        "image_url": recipe.image.url if recipe.image else None,
                    }
                )

            search_results_df = pd.DataFrame(recipe_data)

            # Convert DataFrame to list of dictionaries for template
            search_results_list = search_results_df.to_dict("records")

    # Handle regular search functionality
    elif request.GET and form.is_valid():
        search_performed = True

        # Start with all recipes
        recipes_queryset = Recipe.objects.all()

        # Build search filters based on form data
        search_filters = Q()

        # Recipe name search (partial matching with icontains)
        recipe_name = form.cleaned_data.get("recipe_name")
        if recipe_name:
            search_filters &= Q(name__icontains=recipe_name)

        # Ingredients search (search in related ingredients)
        ingredients = form.cleaned_data.get("ingredients")
        if ingredients:
            # Split comma-separated ingredients and search for each
            ingredient_list = [ing.strip() for ing in ingredients.split(",")]
            ingredient_filters = Q()
            for ingredient in ingredient_list:
                if ingredient:
                    ingredient_filters |= Q(ingredients__name__icontains=ingredient)
            search_filters &= ingredient_filters

        # Category filter
        category = form.cleaned_data.get("category")
        if category:
            search_filters &= Q(category=category)

        # Store difficulty for later filtering (after we get the results)
        difficulty_filter = form.cleaned_data.get("difficulty")

        # Maximum cooking time filter
        max_cooking_time = form.cleaned_data.get("max_cooking_time")
        if max_cooking_time:
            search_filters &= Q(prep_time__lte=max_cooking_time) & Q(
                cooking_time__lte=max_cooking_time
            )

        # Servings range filter
        min_servings = form.cleaned_data.get("min_servings")
        if min_servings:
            search_filters &= Q(servings__gte=min_servings)

        max_servings = form.cleaned_data.get("max_servings")
        if max_servings:
            search_filters &= Q(servings__lte=max_servings)

        # Apply all filters to queryset
        if search_filters:
            recipes_queryset = recipes_queryset.filter(search_filters)

        # Remove duplicates that might occur from ingredient joins
        recipes_queryset = recipes_queryset.distinct()

        # Count results
        results_count = recipes_queryset.count()

        # Convert QuerySet to pandas DataFrame for table display
        if results_count > 0:
            # Prepare data for DataFrame
            recipe_data = []
            for recipe in recipes_queryset.select_related():
                # Apply difficulty filtering here using the actual recipe.difficulty property
                if difficulty_filter and recipe.difficulty != difficulty_filter:
                    continue

                recipe_data.append(
                    {
                        "id": recipe.id,
                        "name": recipe.name,
                        "category": recipe.get_category_display(),
                        "difficulty": recipe.difficulty,
                        "prep_time": recipe.prep_time,
                        "cooking_time": recipe.cooking_time,
                        "total_time": recipe.total_time,
                        "servings": recipe.servings,
                        "description": (
                            recipe.description[:100] + "..."
                            if len(recipe.description) > 100
                            else recipe.description
                        ),
                        "image_url": recipe.image.url if recipe.image else None,
                    }
                )

            # Update results count after difficulty filtering
            results_count = len(recipe_data)

            # Create pandas DataFrame only if we have data
            if recipe_data:
                search_results_df = pd.DataFrame(recipe_data)

                # Sort by relevance (name matches first, then by total time)
                if recipe_name:
                    # Put exact matches first, then partial matches
                    search_results_df["exact_match"] = (
                        search_results_df["name"].str.lower() == recipe_name.lower()
                    )
                    search_results_df = search_results_df.sort_values(
                        ["exact_match", "total_time"], ascending=[False, True]
                    )
                    search_results_df = search_results_df.drop("exact_match", axis=1)
                else:
                    search_results_df = search_results_df.sort_values("total_time")

                # Convert DataFrame to list of dictionaries for template
                search_results_list = search_results_df.to_dict("records")
            else:
                # No results after filtering
                search_results_df = None
                search_results_list = None

    context = {
        "form": form,
        "search_results_df": search_results_df,
        "search_results_list": (
            search_results_list if "search_results_list" in locals() else None
        ),
        "search_performed": search_performed,
        "results_count": results_count,
        "has_results": search_results_df is not None and len(search_results_df) > 0,
    }

    return render(request, "recipes/recipe_search.html", context)
