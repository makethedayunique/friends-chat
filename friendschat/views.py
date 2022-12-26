from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
def _check_user_and_set_session(func):
    """Wrapper function
    
    This function will make sure the user is in authenticated list
    and fetch the avater and set in the session
    """
    def wrapper_func(request, *args, **kwargs):
        self_user = request.user
        # Authenticate whether the user is allowed to login
        extra_info = self_user.socialaccount_set.filter(provider="google")[0].extra_data
        if "profile_pic" not in request.session:
            # Add the picture into the session
            request.session.set_expiry(300) # Set to expire after 5 minutes
            request.session["profile_pic"] = extra_info["picture"]
        return func(request, *args, **kwargs)
    
    return wrapper_func

def chat_login(request):
    """Login Page Get"""
    return render(request, "friendschat/chat_login.html")

@login_required
@_check_user_and_set_session
def chat_board(request):
    """After login, show the chat board"""
    return render(request, "friendschat/chat_app.html")

@login_required
def chat_logout(request):
    """Logout the user and return to the login page"""
    logout(request)
    return redirect(reverse("login"))
