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
    