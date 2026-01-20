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
    # Recipe detail page
    path("recipes/<int:id>/", views.recipe_detail, name="recipe_detail"),
]
