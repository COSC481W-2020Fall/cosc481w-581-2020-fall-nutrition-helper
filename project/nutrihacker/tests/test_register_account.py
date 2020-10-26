from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User

# tests if account is created and user is logged in automatically afterwards
# validation is django default, so not tested
class RegisterAccountTests(TestCase):
    def test_account_created(self):
        response = self.client.post(reverse('nutrihacker:register_account'), {'username': 'test', 'password1': 'djangotests54321', 'password2': 'djangotests54321'}, follow=True)
        # user created
        self.assertQuerysetEqual(User.objects.all(), ['<User: test>'])
        # user logged in
        self.assertIn('_auth_user_id', self.client.session)
    
    def test_password_mismatch(self):
        response = self.client.post(reverse('nutrihacker:register_account'), {'username': 'test', 'password1': 'djangotests54321', 'password2': 'password'}, follow=True)
        # user not created
        self.assertQuerysetEqual(User.objects.all(), [])
        # user not logged in
        self.assertNotIn('_auth_user_id', self.client.session)
        
    def invalid_password(self):
        response = self.client.post(reverse('nutrihacker:register_account'), {'username': 'test', 'password1': 'password', 'password2': 'password'}, follow=True)
        # user not created
        self.assertQuerysetEqual(User.objects.all(), [])
        # user not logged in
        self.assertNotIn('_auth_user_id', self.client.session)
        