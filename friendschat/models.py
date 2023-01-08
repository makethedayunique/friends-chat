from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChatUser(models.Model):
    """Wrapped user class"""
    google_id = models.CharField(max_length=20, blank=True)
    related_user = models.OneToOneField(User, on_delete=models.PROTECT)
    google_pic = models.CharField(max_length=300, null=True) # Will be reset everytime the user logs in
    friends = models.ManyToManyField("self", default=None)
    email = models.EmailField(null=True, blank=True)
    is_online = models.BooleanField(default=True)
    description = models.CharField(max_length=300, default="This person wrote nothing.", blank=True)

    def __str__(self):
        return 'ChatUser(id=' + str(self.id) +')'

    def get_user_name(self):
        """Get the user full name"""
        return self.related_user.first_name + " " + self.related_user.last_name

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

class ChatMessage(models.Model):
    """Message class"""
    message_key = models.CharField(max_length=100, default=None)
    send_from = models.ForeignKey(ChatUser, on_delete=models.PROTECT, related_name="message_sent")
    send_to = models.ForeignKey(ChatUser, on_delete=models.PROTECT, related_name="message_to")
    send_message = models.TextField(null=True, blank=True, default=None)
    send_time = models.DateTimeField()
    send_file = models.FileField(blank=True, null=True, default=None)
    file_type = models.CharField(blank=True, null=True, default=None, max_length=50)

    def __str__(self):
        return "Message from {} to {}: {}".format(self.send_from.related_user.first_name,
            self.send_to.related_user.first_name, self.send_message)

class FriendRequest(models.Model):
    """Friend request class which is to request the user"""
    request_for = models.ForeignKey(ChatUser, null=True, related_name="requests", on_delete=models.SET_NULL)
    request_from = models.ForeignKey(ChatUser, null=True, on_delete=models.SET_NULL)
    request_time = models.DateTimeField()
