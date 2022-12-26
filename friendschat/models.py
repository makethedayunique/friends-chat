from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChatUser(models.Model):
    google_id = models.CharField(max_length=20, blank=True)
    related_user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="related_user")
    google_pic = models.CharField(max_length=300, null=True) # Will be reset everytime the user logs in
    friends = models.ManyToManyField("self", default=None)
    email = models.EmailField(null=True, blank=True)
    is_online = models.BooleanField(default=True)

    def __str__(self):
        return 'ChatUser(id=' + str(self.id) +')'

    def update(self, commit=False, **kwargs):
        """Update a field value"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if commit:
            # If commit set to be true, save the object
            self.save()

class AuthorizedEmails(models.Model):
    """Authorized Emails to use thie app"""
    email = models.EmailField(default=None, blank=True, null=True)
    email_suffix = models.CharField(max_length=100, default=None, blank=True, null=True)

