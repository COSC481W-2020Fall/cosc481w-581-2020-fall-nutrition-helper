
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from nutrihacker.models import Profile

import datetime
from decimal import Decimal

def login_user(client):
    name = 'test'
    pword = 'djangotest159'
    user = User.objects.create_user(name, password=pword)
    client.login(username=name, password=pword)
    return user
        
    
class AddProfileTests(TestCase):
    def test_update_metric(self):
        
        user = login_user(self.client)
        
        bdate = datetime.datetime(1991, 1, 1)
        testProfile = Profile.objects.get(user=user)
        testProfile.gender = 'F'
        testProfile.birthdate = bdate
        testProfile.set_height(153.67)
        testProfile.set_weight(63.77)
        testProfile.save()
        
        self.assertEqual(testProfile.gender, 'F')
        self.assertEqual(testProfile.birthdate, bdate)
        self.assertEqual(testProfile.get_height(), 153.67)
        self.assertEqual(testProfile.get_weight(), 63.77)
        self.assertEqual(testProfile.showmetric, True)
        
    def test_update_imperial(self):
        
        user = login_user(self.client)
        
        bdate = datetime.datetime(1991, 1, 1)
        testProfile = Profile.objects.get(user=user)
        testProfile.showmetric = False
        testProfile.gender = 'F'
        testProfile.birthdate = bdate
        testProfile.set_height(60.5)
        testProfile.set_weight(140.6)
        testProfile.save()
        
        self.assertEqual(testProfile.gender, 'F')
        self.assertEqual(testProfile.birthdate, bdate)
        self.assertEqual(testProfile.get_height(), round(Decimal(60.5), 2))
        self.assertEqual(testProfile.get_weight(), round(Decimal(140.6), 2))
        self.assertEqual(testProfile.showmetric, False)
               
    def test_delete(self):
        
        user = login_user(self.client)
        Profile.objects.filter(id=user.id).delete()

        try: 
            with self.assertRaises(ObjectDoesNotExist) as cm:
                Profile.objects.get(user=user)
        except AssertionError as e:
            raise e
