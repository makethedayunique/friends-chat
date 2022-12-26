from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from friendschat.models import AuthorizedEmails

from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import render

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Inherit from the default addapter to restrict user login"""
    def is_open_for_signup(self, request, sociallogin):
        self_email = sociallogin.user.email
        authenticated = True
        try:
            single_email = AuthorizedEmails.objects.get(email=self_email)
        except AuthorizedEmails.DoesNotExist:
            authenticated = False
        except AuthorizedEmails.MultipleObjectsReturned:
            pass

        if not authenticated:
            self_suffix = self_email[self_email.index("@"):]
            try:
                single_suffix = AuthorizedEmails.objects.get(email_suffix=self_suffix)
                authenticated = True
            except AuthorizedEmails.DoesNotExist:
                pass
            except AuthorizedEmails.MultipleObjectsReturned:
                authenticated = True
        if not authenticated:
            raise ImmediateHttpResponse(render(request, "friendschat/chat_login.html", 
                {"error": "You are not authorized to log in"}))
        return authenticated
        