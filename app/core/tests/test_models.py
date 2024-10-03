"""
Tests for models
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

class ModelTests(TestCase):
    """Testing models"""

    def test_create_user_with_email_successful(self):
        """test creating user model using email successfully"""

        email = 'test@example.com'
        password = 'testpass@123'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_normalised_email(self):
        """test creating user with normalised email"""

        test_data = [
            ['Person_name@COMPANY.com', 'Person_name@company.com'],
            ['person_name@CompanY.coM', 'person_name@company.com'],
            ['Person_Name@company.Com', 'Person_Name@company.com']
        ]

        for input_email, normalised_email in test_data:
            user = get_user_model().objects.create_user(input_email, 'sample_password')
            self.assertEqual(user.email, normalised_email)

    def test_create_user_without_email(self):
        """test_creating user_without_email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample_password')
    
    def test_create_superuser(self):
        """test creating super user"""

        user = get_user_model().objects.create_superuser('superuser@example.com', 'samplePass')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_create_recipe(self):
        """Test create recipe object"""
        user = get_user_model().objects.create_user(
            email = 'test1@user.com',
            password = 'test1234'
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title = 'Sample Recipe 1',
            time_minutes = 5,
            description = 'Sample Recipe 1 Description',
            price = Decimal('5.50')
        )

        self.assertEqual(str(recipe), recipe.title)