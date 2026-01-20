from django.contrib import admin
from .models import Ingredient


#This adds a search bar to the Ingredient admin page
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    
#Register with the custom admin class 
admin.site.register(Ingredient, IngredientAdmin)