from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from nutrihacker.models import Profile

from datetime import datetime

def login_user(client):
    name = 'test'
    pword = 'djangotest159'
    user = User.objects.create_user(name, password=pword)
    client.login(username=name, password=pword)
    return user
    
class AddProfileTests(TestCase):
    def test_add(self):
        user = login_user(self.client)
        bdate = datetime.datetime(1991, 1, 1)
        Profile.objects.create(user=user, gender='F', birthdate=bdate, height=60.5, weight=140.6)
        
        testProfile = Profile.objects.get(user=user)
        
        self.assertEqual(testProfile.gender, 'F')
        self.assertEqual(testProfile.birthdate, bdate)
        self.assertEqual(testProfile.height, 60.5)
        self.assertEqual(testProfile.weight, 140.6)
               
