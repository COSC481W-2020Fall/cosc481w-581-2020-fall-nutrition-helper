from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from nutrihacker.models import Allergy, DietPreference, Profile

def login_user(client):
    name = 'test'
    pword = 'djangotest159'
    user = User.objects.create_user(name, password=pword)
    client.login(username=name, password=pword)
    return user
    
def create_allergies(profile):
    names = ['Peanut Allergy', 'Fish Allergy', 'Milk Allergy']
    for allergy_name in names:
        allergy = Allergy.objects.create(name=allergy_name)
        allergy.profiles.add(profile)
        
def create_diets(profile):
    names = ['Vegetarian', 'Vegan', 'Pescatarian']
    for diet_name in names:
        diet = DietPreference.objects.create(name=diet_name)
        diet.profiles.add(profile)

class AddAllergyTests(TestCase):
    # checks if allergy is added and if redirected back to diet_and_allergies page
    def test_add(self):
        allergy_name = 'Peanut Allergy'
        Allergy.objects.create(name=allergy_name)
        user = login_user(self.client)
        response = self.client.post(reverse('nutrihacker:add_allergy'), {'allergy_select': 1}, follow=True)
        self.assertQuerysetEqual(Allergy.objects.filter(profiles = Profile.objects.get(user=user)), ['<Allergy: ' + allergy_name + '>'])
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
    # attempts to adds allergy that doesn't exist
    def test_bad_form(self):
        user = login_user(self.client)
        response = self.client.post(reverse('nutrihacker:add_allergy'), {'allergy_select': 99}, follow=True)
        self.assertQuerysetEqual(Allergy.objects.filter(profiles = Profile.objects.get(user=user)), [])
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
    # get request, should redirect back to diet_and_allergies page
    def test_get(self):
        user = login_user(self.client)
        response = self.client.get(reverse('nutrihacker:add_allergy'), follow=True)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
        
class AddDietPreferenceTests(TestCase):
    # checks if diet preference is added and if redirected back to diet_and_allergies page
    def test_add(self):
        diet_name = 'Vegetarian'
        DietPreference.objects.create(name=diet_name)
        user = login_user(self.client)
        response = self.client.post(reverse('nutrihacker:add_diet_preference'), {'diet_select': 1}, follow=True)
        self.assertQuerysetEqual(DietPreference.objects.filter(profiles = Profile.objects.get(user=user)), ['<DietPreference: ' + diet_name + '>'])
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
    # attempts to adds diet preference that doesn't exist
    def test_bad_form(self):
        user = login_user(self.client)
        response = self.client.post(reverse('nutrihacker:add_diet_preference'), {'diet_select': 99}, follow=True)
        self.assertQuerysetEqual(DietPreference.objects.filter(profiles = Profile.objects.get(user=user)), [])
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
    # get request, should redirect back to diet_and_allergies page
    def test_get(self):
        user = login_user(self.client)
        response = self.client.get(reverse('nutrihacker:add_diet_preference'), follow=True)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])

class DeleteAllergyTests(TestCase):
    def test_delete_single(self):
        user = login_user(self.client)
        create_allergies(Profile.objects.get(user=user))
        response = self.client.post(reverse('nutrihacker:delete_allergy'), {'allergy_checkbox': [1]}, follow=True)
        self.assertQuerysetEqual(Allergy.objects.filter(profiles = Profile.objects.get(user=user)), ['<Allergy: Fish Allergy>', '<Allergy: Milk Allergy>'], ordered=False)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)]) 
    def test_delete_multiple(self):
        user = login_user(self.client)
        create_allergies(Profile.objects.get(user=user))
        response = self.client.post(reverse('nutrihacker:delete_allergy'), {'allergy_checkbox': [2,3]}, follow=True)
        self.assertQuerysetEqual(Allergy.objects.filter(profiles = Profile.objects.get(user=user)), ['<Allergy: Peanut Allergy>'])
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)]) 
    def test_bad_form(self):
        user = login_user(self.client)
        create_allergies(Profile.objects.get(user=user))
        response = self.client.post(reverse('nutrihacker:delete_allergy'), {'fake': 99}, follow=True)
        self.assertQuerysetEqual(Allergy.objects.filter(profiles = Profile.objects.get(user=user)), ['<Allergy: Peanut Allergy>', '<Allergy: Fish Allergy>', '<Allergy: Milk Allergy>'], ordered=False)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
    def test_get(self):
        user = login_user(self.client)
        response = self.client.get(reverse('nutrihacker:delete_allergy'), follow=True)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])

class DeleteDietPreferenceTests(TestCase):
    def test_delete_single(self):
        user = login_user(self.client)
        create_diets(Profile.objects.get(user=user))
        response = self.client.post(reverse('nutrihacker:delete_diet_preference'), {'diet_checkbox': [1]}, follow=True)
        self.assertQuerysetEqual(DietPreference.objects.filter(profiles = Profile.objects.get(user=user)), ['<DietPreference: Vegan>', '<DietPreference: Pescatarian>'], ordered=False)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)]) 
    def test_delete_multiple(self):
        user = login_user(self.client)
        create_diets(Profile.objects.get(user=user))
        response = self.client.post(reverse('nutrihacker:delete_diet_preference'), {'diet_checkbox': [2,3]}, follow=True)
        self.assertQuerysetEqual(DietPreference.objects.filter(profiles = Profile.objects.get(user=user)), ['<DietPreference: Vegetarian>'])
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)]) 
    def test_bad_form(self):
        user = login_user(self.client)
        create_diets(Profile.objects.get(user=user))
        response = self.client.post(reverse('nutrihacker:delete_diet_preference'), {'fake': 99}, follow=True)
        self.assertQuerysetEqual(DietPreference.objects.filter(profiles = Profile.objects.get(user=user)), ['<DietPreference: Vegetarian>', '<DietPreference: Vegan>', '<DietPreference: Pescatarian>'], ordered=False)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
    def test_get(self):
        user = login_user(self.client)
        response = self.client.get(reverse('nutrihacker:delete_diet_preference'), follow=True)
        self.assertEqual(response.redirect_chain, [(reverse('nutrihacker:diet_and_allergies'), 302)])
    