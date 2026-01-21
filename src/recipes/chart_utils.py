import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from collections import Counter
from django.db.models import Count
import pandas as pd

# Use non-interactive backend for server environments
matplotlib.use("Agg")


def generate_chart_image(fig):
    """Convert matplotlib figure to base64 string for embedding in HTML."""
    buffer = io.BytesIO()
    fig.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
        dpi=150,
        facecolor="white",
        edgecolor="none",
    )
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    plt.close(fig)
    return image_base64


def create_ingredients_bar_chart(user_favorites):
    """Create bar chart showing most common ingredients in user's saved recipes."""
    if not user_favorites:
        return None

    # Collect all ingredients from saved recipes
    ingredient_counts = Counter()
    for favorite in user_favorites:
        recipe_ingredients = favorite.recipe.ingredients.all()
        for ingredient in recipe_ingredients:
            ingredient_counts[ingredient.name] += 1

    if not ingredient_counts:
        return None

    # Get top 10 most common ingredients
    top_ingredients = ingredient_counts.most_common(10)
    if not top_ingredients:
        return None

    ingredients, counts = zip(*top_ingredients)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bar chart with styling
    bars = ax.bar(ingredients, counts, color="#2c3e50", alpha=0.8)

    # Customize the chart
    ax.set_title(
        "Most Common Ingredients in Your Saved Recipes",
        fontsize=16,
        fontweight="bold",
        color="#2c3e50",
        pad=20,
    )
    ax.set_xlabel("Ingredients", fontsize=12, color="#495057")
    ax.set_ylabel("Number of Saved Recipes", fontsize=12, color="#495057")

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")

    # Add value labels on top of bars
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            str(count),
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # Style the chart
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Adjust layout
    plt.tight_layout()

    return generate_chart_image(fig)


def create_categories_pie_chart(user_favorites):
    """Create pie chart showing distribution of saved recipes by category."""
    if not user_favorites:
        return None

    # Count recipes by category
    category_counts = Counter()
    for favorite in user_favorites:
        category_display = favorite.recipe.get_category_display()
        category_counts[category_display] += 1

    if not category_counts:
        return None

    categories = list(category_counts.keys())
    counts = list(category_counts.values())

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))

    # Define colors that match the site's color scheme
    colors = [
        "#2c3e50",
        "#34495e",
        "#7f8c8d",
        "#95a5a6",
        "#bdc3c7",
        "#ecf0f1",
        "#e74c3c",
        "#c0392b",
        "#f39c12",
        "#f1c40f",
    ]

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=categories,
        autopct="%1.1f%%",
        colors=colors[: len(categories)],
        startangle=90,
        textprops={"fontsize": 11},
    )

    # Customize the chart
    ax.set_title(
        "Your Saved Recipe Categories",
        fontsize=16,
        fontweight="bold",
        color="#2c3e50",
        pad=20,
    )

    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(10)

    # Equal aspect ratio ensures pie chart is circular
    ax.axis("equal")

    return generate_chart_image(fig)


def create_cooking_time_line_chart(user_favorites):
    """Create line chart showing cooking time preferences."""
    if not user_favorites:
        return None

    # Define time ranges
    time_ranges = ["0-15 min", "16-30 min", "31-60 min", "60+ min"]
    range_counts = [0, 0, 0, 0]

    # Categorize recipes by total cooking time
    for favorite in user_favorites:
        total_time = favorite.recipe.total_time
        if total_time <= 15:
            range_counts[0] += 1
        elif total_time <= 30:
            range_counts[1] += 1
        elif total_time <= 60:
            range_counts[2] += 1
        else:
            range_counts[3] += 1

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create line chart with markers
    line = ax.plot(
        time_ranges,
        range_counts,
        marker="o",
        linewidth=3,
        markersize=8,
        color="#2c3e50",
        markerfacecolor="#e74c3c",
    )

    # Customize the chart
    ax.set_title(
        "Your Saved Recipes by Cooking Time",
        fontsize=16,
        fontweight="bold",
        color="#2c3e50",
        pad=20,
    )
    ax.set_xlabel("Total Cooking Time (minutes)", fontsize=12, color="#495057")
    ax.set_ylabel("Number of Saved Recipes", fontsize=12, color="#495057")

    # Add value labels on data points
    for i, count in enumerate(range_counts):
        ax.text(
            i,
            count + max(range_counts) * 0.02,
            str(count),
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    # Style the chart
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Set y-axis to start from 0 and add some padding
    ax.set_ylim(0, max(range_counts) * 1.15 if max(range_counts) > 0 else 1)

    # Adjust layout
    plt.tight_layout()

    return generate_chart_image(fig)


def generate_all_saved_recipe_charts(user):
    """Generate all three charts for a user's saved recipes."""
    if not user.is_authenticated:
        return {
            "ingredients_chart": None,
            "categories_chart": None,
            "cooking_time_chart": None,
        }

    try:
        # Get user's saved recipes
        user_favorites = user.favorites.select_related("recipe").prefetch_related(
            "recipe__ingredients"
        )

        # Only generate charts if user has saved recipes
        if not user_favorites.exists():
            return {
                "ingredients_chart": None,
                "categories_chart": None,
                "cooking_time_chart": None,
            }

        # Generate all charts
        charts = {
            "ingredients_chart": create_ingredients_bar_chart(user_favorites),
            "categories_chart": create_categories_pie_chart(user_favorites),
            "cooking_time_chart": create_cooking_time_line_chart(user_favorites),
        }

        return charts

    except Exception as e:
        # Log the error in production, return empty charts for now
        print(f"Chart generation error: {e}")
        return {
            "ingredients_chart": None,
            "categories_chart": None,
            "cooking_time_chart": None,
        }
