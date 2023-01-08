from allauth.account.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth import logout
from django.shortcuts import render
from allauth.exceptions import ImmediateHttpResponse
from friendschat.models import ChatUser

def _create_and_get_chatuser(request, user, google_info):
    """Get or create a new chatuser"""
    chat_user = None
    try:
        chat_user = ChatUser.objects.get(related_user=user)
    except ChatUser.DoesNotExist:
        # Create a new chat user
        chat_user = ChatUser(
            google_id = google_info["id"],
            related_user = user,
            google_pic = google_info["picture"],
            email = google_info["email"],
            is_online = True
        )
        chat_user.save()
    except:
        # Other exceptions
        logout(user)
        raise ImmediateHttpResponse(render(request, "friendschat/chat_login.html", 
            {"error": "You are not authorized to log in"}))
    return chat_user

@receiver(user_logged_in)
def post_login(sender, request, user, **kwargs):
    """Handle when a user successfully logged in"""
    # Check whether there is chat user in the database
    google_info = user.socialaccount_set.filter(provider="google")[0].extra_data
    chat_user = _create_and_get_chatuser(request, user, google_info)
    chat_user.update(commit=True, google_pic=google_info["picture"]) # Update the picture
    chat_user.update(commit=True, is_online=True)

@receiver(user_logged_out)
def post_logout(sender, request, user, **kwargs):
    """Handle when a user log out"""
    google_info = user.socialaccount_set.filter(provider="google")[0].extra_data
    chat_user = _create_and_get_chatuser(request, user, google_info)
    chat_user.update(commit=True, is_online=False) # Update the status

