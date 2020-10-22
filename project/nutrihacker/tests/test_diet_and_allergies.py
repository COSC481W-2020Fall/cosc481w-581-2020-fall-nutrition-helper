from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from nutrihacker.models import Allergy, Profile

def login_user(client):
    name = 'test'
    pword = 'djangotest159'
    user = User.objects.create_user(name, password=pword)
    client.login(username=name, password=pword)
    return user
    
class AddAllergyViewTests(TestCase):
    def test_add(self):
        test_name = 'Peanut Allergy'
        Allergy.objects.create(name=test_name)
        user = login_user(self.client)
        self.client.post(reverse('nutrihacker:add_allergy'), {'allergy_select': 1})
        self.assertQuerysetEqual(Allergy.objects.filter(profiles = Profile.objects.get(user=user)), map(repr, Allergy.objects.filter(name=test_name)))
    