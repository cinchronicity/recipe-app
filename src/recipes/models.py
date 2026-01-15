from django.db import models
# Recipes depend on Ingredients model so must import it 
from ingredients.models import Ingredient


# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    cooking_time = models.PositiveIntegerField(help_text="Time in minutes")
    ingredients = models.ManyToManyField(Ingredient, related_name="recipes")

    def __str__(self):
        return self.name
