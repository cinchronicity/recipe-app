from django.shortcuts import render

# Create your views here.

# This view handles the homepage request.
# It receives the HTTP request and returns an HTML response.
def home(request):
    return render(request, "recipes/recipes_home.html")
