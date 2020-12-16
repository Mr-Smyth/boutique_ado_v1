# import our settings from django.conf
from django.conf import settings
# import the S3Boto3Storage class
from storages.backends.s3boto3 import S3Boto3Storage


# create a custom class that inherits the s3boto class we imported
# and tell it that we want to store static files in a location from the
# settings.py
class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


# create a custom class that inherits the s3boto class we imported
# and tell it that we want to store media files in a location from the
# settings.py
class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
