from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from nutrihacker.models import Profile

from datetime import datetime
from decimal import Decimal

def login_user(client):
    name = 'test'
    pword = 'djangotest159'
    user = User.objects.create_user(name, password=pword)
    client.login(username=name, password=pword)
    return user
    
class UpdateProfileTests(TestCase):
    def test_update_profile_metric(self):
        user = login_user(self.client)
        bdate = '2006-10-25'
        self.client.post(reverse('nutrihacker:update_profile'), {'first_name': 'django', 'last_name': 'test',  'email': 'test@gmail.com', 'gender': 'M', 'birthdate':bdate, 'height': 152.4, 'weight': 65, 'showmetric': True})
        profile = Profile.objects.get(user=user)
        updated_user = User.objects.get(profile=profile)
        self.assertEqual(updated_user.first_name, 'django')
        self.assertEqual(updated_user.last_name, 'test')
        self.assertEqual(updated_user.email, 'test@gmail.com')
        self.assertEqual(profile.gender, 'M')
        self.assertEqual(str(profile.birthdate), bdate)
        self.assertEqual(profile.get_height(), Decimal('152.4'))
        self.assertEqual(profile.get_weight(), Decimal('65'))
        self.assertEqual(profile.showmetric, True)
    
    def test_update_profile_imperial(self):
        user = login_user(self.client)
        bdate = '2006-10-25'
        self.client.post(reverse('nutrihacker:update_profile'), {'first_name': 'django', 'last_name': 'test',  'email': 'test@gmail.com', 'gender': 'M', 'birthdate':bdate, 'height': 60, 'weight': 143.3, 'showmetric': False})
        profile = Profile.objects.get(user=user)
        updated_user = User.objects.get(profile=profile)
        self.assertEqual(updated_user.first_name, 'django')
        self.assertEqual(updated_user.last_name, 'test')
        self.assertEqual(updated_user.email, 'test@gmail.com')
        self.assertEqual(profile.gender, 'M')
        self.assertEqual(str(profile.birthdate), bdate)
        self.assertEqual(profile.get_height(), Decimal('60.00'))
        self.assertEqual(profile.get_weight(), Decimal('143.30'))
        self.assertEqual(profile.showmetric, False)
        
    def test_update_profile_bad_form(self):
        user = login_user(self.client)
        bdate = '2006-10-25'
        self.client.post(reverse('nutrihacker:update_profile'), {'first_name': 'django', 'last_name': 'test',  'email': 'email', 'gender': 'M', 'birthdate':bdate, 'height': 'a', 'weight': 'b', 'showmetric': False})
        profile = Profile.objects.get(user=user)
        updated_user = User.objects.get(profile=profile)
        self.assertNotEqual(updated_user.first_name, 'django')
        self.assertNotEqual(updated_user.last_name, 'test')
        self.assertNotEqual(updated_user.email, 'email')
        self.assertNotEqual(profile.gender, 'M')
        self.assertNotEqual(str(profile.birthdate), bdate)
        self.assertNotEqual(profile.get_height(), 'a')
        self.assertNotEqual(profile.get_weight(), 'b')
        self.assertNotEqual(profile.showmetric, False)
    
    
