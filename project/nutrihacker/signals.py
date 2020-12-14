from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

# whenever a user is created, create a profile related to it
@receiver(post_save, sender=User, dispatch_uid="create_profile")
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# after a user is created, save a profile related to it
@receiver(post_save, sender=User, dispatch_uid="save_profile")
def save_profile(sender, instance, **kwargs):
    instance.profile.save()