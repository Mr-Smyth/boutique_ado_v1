from django.db import models

# import the user model
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField

class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """
    # like a foreign key - except that it specifies that each user can only
    # have one profile and each profile can only be attached to one user
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # the rest of the fields in this model are the delivery information fields
    # that we want the user to provide defaults for.
    # These can come directly from the order model inside checkout

    # we want the fields to be optional so set blank = True
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country *', null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)


    # string method to return the users name
    def __str__(self):
        return self.user.username

# a receiver for the post_save event from the user model
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    A receiver for the post save event from the user model.
    So that each time a user object is saved. We'll automatically either
    create a profile for them if the user has just been created.
    Or just save the profile to update it if the user already existed.
    In this case by the way, since there's only one signal I'm not putting
    it in a separate signals.py module like we did for the ones on the
    order model.
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
