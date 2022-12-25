from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.

def chat_login(request):
    """Login Page Get"""
    return render(request, "friendschat/chat_login.html")

@login_required
def chat_board(request):
    """After login, show the chat board"""
    print("Come Here")
    return render(request, "friendschat/chat_app.html")

@login_required
def chat_logout(request):
    """Logout the user and return to the login page"""
    logout(request)
    redirect(reverse("login"))
    