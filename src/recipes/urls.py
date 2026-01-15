from django.urls import path
from . import views
# Maps URLs to views inside the recipes app.
# App namespace — useful later when referencing URLs
app_name = "recipes"

urlpatterns = [
    # When someone visits the root URL (""), call the home view
    path("", views.home, name="home"),
]
