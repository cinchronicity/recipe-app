from django.urls import path
from . import views

# Maps URLs to views inside the recipes app.
# App namespace — useful later when referencing URLs
app_name = "recipes"

urlpatterns = [
    # When someone visits the root URL (""), call the home view
    path("", views.home, name="home"),
    # Recipes list page
    path("recipes/", views.recipes_list, name="recipes_list"),
    # Recipe search page
    path("search/", views.recipe_search, name="recipe_search"),
    # Recipe detail page
    path("recipes/<int:id>/", views.recipe_detail, name="recipe_detail"),
    # User favorites page (requires login)
    path("favorites/", views.favorites_list, name="favorites_list"),
    # Add/remove favorites (requires login)
    path("favorites/add/<int:recipe_id>/", views.add_favorite, name="add_favorite"),
    path(
        "favorites/remove/<int:recipe_id>/",
        views.remove_favorite,
        name="remove_favorite",
    ),
]
