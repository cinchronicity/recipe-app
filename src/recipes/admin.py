from django.contrib import admin
from .models import Recipe, Favorite


# Add admin class before registering the model
class RecipeAdmin(admin.ModelAdmin):
    # makes the list page more useful
    list_display = (
        "name",
        "category",
        "servings",
        "prep_time",
        "cooking_time",
        "created_at",
    )
    list_filter = ("category",)
    search_fields = ("name", "description", "instructions")


# Register the Recipe model with the custom admin class
admin.site.register(Recipe, RecipeAdmin)


# Admin configuration for Favorite model
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "recipe__name")


admin.site.register(Favorite, FavoriteAdmin)
