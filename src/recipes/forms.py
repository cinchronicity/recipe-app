from django import forms
from .models import Recipe


class RecipeSearchForm(forms.Form):
    """Form for searching recipes with multiple criteria."""

    # Recipe name search with partial matching
    recipe_name = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search recipe name...",
                "class": "form-control search-input",
            }
        ),
        label="Recipe Name",
    )

    # Ingredient search
    ingredients = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. chicken, tomato, garlic",
                "class": "form-control search-input",
            }
        ),
        label="Ingredients",
        help_text="Enter ingredient names (comma-separated for multiple)",
    )

    # Category dropdown
    category = forms.ChoiceField(
        choices=[("", "All Categories")] + Recipe.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control search-select"}),
        label="Category",
    )

    # Difficulty level
    difficulty = forms.ChoiceField(
        choices=[
            ("", "All Difficulties"),
            ("Easy", "Easy"),
            ("Medium", "Medium"),
            ("Hard", "Hard"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control search-select"}),
        label="Difficulty Level",
    )

    # Maximum cooking time
    max_cooking_time = forms.IntegerField(
        min_value=1,
        max_value=480,  # 8 hours max
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Max minutes",
                "class": "form-control search-input",
                "min": "1",
                "max": "480",
            }
        ),
        label="Maximum Cooking Time (minutes)",
        help_text="Enter maximum total cooking time in minutes",
    )

    # Servings range
    min_servings = forms.IntegerField(
        min_value=1,
        max_value=20,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Min servings",
                "class": "form-control search-input",
                "min": "1",
                "max": "20",
            }
        ),
        label="Minimum Servings",
    )

    max_servings = forms.IntegerField(
        min_value=1,
        max_value=20,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Max servings",
                "class": "form-control search-input",
                "min": "1",
                "max": "20",
            }
        ),
        label="Maximum Servings",
    )

    def clean(self):
        """Custom validation to ensure min_servings <= max_servings."""
        cleaned_data = super().clean()
        min_servings = cleaned_data.get("min_servings")
        max_servings = cleaned_data.get("max_servings")

        if min_servings and max_servings and min_servings > max_servings:
            raise forms.ValidationError(
                "Minimum servings cannot be greater than maximum servings."
            )

        return cleaned_data

    def has_search_criteria(self):
        """Check if any search criteria are provided."""
        if not self.is_valid():
            return False

        return any(
            [
                self.cleaned_data.get("recipe_name"),
                self.cleaned_data.get("ingredients"),
                self.cleaned_data.get("category"),
                self.cleaned_data.get("difficulty"),
                self.cleaned_data.get("max_cooking_time"),
                self.cleaned_data.get("min_servings"),
                self.cleaned_data.get("max_servings"),
            ]
        )
