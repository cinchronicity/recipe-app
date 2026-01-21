from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from recipes.models import Recipe, Favorite


def login_view(request):
    """Handle user login."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Redirect to next page if specified, otherwise to recipes list
            next_page = request.GET.get("next", "recipes:recipes_list")
            return redirect(next_page)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def logout_view(request):
    from django.contrib.auth import logout

    # Clear any existing messages first (like favorite confirmations)
    storage = messages.get_messages(request)
    for message in storage:
        pass  # This consumes and clears all messages

    logout(request)
    return redirect("accounts:logout_success")


def logout_success(request):
    """Display logout success page with featured content."""
    # Get a random featured recipe
    featured_recipe = Recipe.objects.order_by("?").first()

    # Get some stats for the page
    total_recipes = Recipe.objects.count()
    total_users = User.objects.count()
    total_favorites = Favorite.objects.count()

    context = {
        "featured_recipe": featured_recipe,
        "total_recipes": total_recipes,
        "total_users": total_users,
        "total_favorites": total_favorites,
    }
    return render(request, "accounts/success.html", context)
