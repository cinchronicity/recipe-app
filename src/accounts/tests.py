from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from recipes.models import Recipe, Favorite
from ingredients.models import Ingredient


class AccountsViewTests(TestCase):
    """Test cases for accounts app views and authentication flow."""

    def setUp(self):
        """Set up test data for accounts tests."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = Client()

    def test_login_view_get(self):
        """Test that login view renders correctly."""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
        self.assertContains(response, "username")
        self.assertContains(response, "password")

    def test_login_view_template(self):
        """Test that login view uses correct template."""
        response = self.client.get(reverse("accounts:login"))
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_valid_login_post(self):
        """Test login with valid credentials."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )

        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)

    def test_invalid_login_post(self):
        """Test login with invalid credentials."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )

        # Should stay on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_login_redirect_to_next(self):
        """Test login redirects to next parameter if provided."""
        next_url = reverse("recipes:favorites_list")
        response = self.client.post(
            f"{reverse('accounts:login')}?next={next_url}",
            {"username": "testuser", "password": "testpass123"},
        )

        self.assertRedirects(response, next_url)

  
    def test_login_already_authenticated_redirect(self):
        """Test that already logged-in users are handled appropriately."""
        # Login the user first
        self.client.login(username="testuser", password="testpass123")

        # Try to access login page
        response = self.client.get(reverse("accounts:login"))

        # Should still be accessible (allowing re-login)
        self.assertEqual(response.status_code, 200)

