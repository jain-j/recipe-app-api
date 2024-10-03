"""
Test django admin customization
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client 

class AdminSiteTests(TestCase):
    """Tests Django Admin customisation"""

    def setUp(self):
        """Create Users and setup by force login"""
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(email='admin@admin.com', password='testadmin123')

        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(email='user@example.com', password='testuser123', name='Test user')
    
    def test_users_list(self):
        """Test users listed on page"""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
    
    def test_edit_user_page(self):
        """Test Edit user page of admin"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
    
    def test_create_user_page(self):
        """Test create user page for admin"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)