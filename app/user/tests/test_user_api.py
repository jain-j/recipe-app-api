"""
Testsfor User API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """ Helper function to create and reuturn new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Tests User API having Public access"""

    def setUp(self):
        self.client = APIClient()
    
    def test_user_create_sucessfully(self):
        """Tests user created successfully with correct data"""
        payload = {
            'email' : 'test1@example.com',
            'password' : 'test@123',
            'name' : 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
    
    def test_user_create_failed_email_exists(self):
        """Tests user error with existing email"""
        payload = {
            'email' : 'test1@example.com',
            'password' : 'test@123',
            'name' : 'Test User',
        }
        
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_password_short(self):
        """Test user given short password"""

        payload = {
            'email' : 'test1@example.com',
            'password' : 'test',
            'name' : 'Test User',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_created = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_created)

    def test_create_token_for_user(self):
        """Testing token API"""
        user_details = {
            'name': 'Test Name',
            'email': 'testuser@example.com',
            'password': 'test1234'
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        
    
    def test_token_bad_credetails(self):
        """failing tets case for toeken"""

        create_user(email='testuser@example.com', password='goodpass')

        payload = {'email':'testuser@example2.com', 'password': 'wrongpass'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_from_blank_password(self):
        """creating token with blank password"""
        payload = {'email':'testuser@example2.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_profile_without_auth(self):
        """Test me url without auth"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Tests private user API"""

    def setUp(self):
        self.user = create_user(
            name = 'Test User',
            email = 'test@user.com',
            password = 'Jin12345'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_profile(self):
        """test me URL"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
    
    def test_post_on_me(self):
        """testpost method on me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)