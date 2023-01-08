from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from friendschat.models import ChatMessage, ChatUser, FriendRequest

import json

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
            request.session.set_expiry(3000) # Set to expire after 5 minutes
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
    if request.method == "GET":
        # Get the chat list with friends
        content = {
            "friends": [],
            "chat_list": [],
        }
        chat_user = _get_google_user(request.user)
        if chat_user is None:
            return render(request, "friendschat/chat_error.html",
                {"error_code": "404", "error_msg": "Related Google user not found!"})
        for friend in chat_user.friends.all():
            friend_response = {
                "friend_id": friend.related_user.id,
                "friend_name": friend.get_user_name(),
                "online": friend.is_online,
                "friend_pic": friend.google_pic,
            }
            content["friends"].append(friend_response)
            chat_with_friend = {
                "friend_id": friend.related_user.id,
                "friend_name": friend.get_user_name(),
                "friend_pic": friend.google_pic,
                "online": friend.is_online,
                "batch_id": 0,
                "friend_desc": friend.description,
                "messages": []
            }
            # Get the first 10 batch
            messages = get_message_batch(request, chat_user, friend, 0)
            for i in range(len(messages)-1, -1, -1):
                msg = messages[i]
                chat_with_friend["messages"].append({
                    "message_id": msg.id,
                    "message_my_sent": msg.send_from == chat_user,
                    "message_sent_pic": msg.send_from.google_pic,
                    "message_datetime": msg.send_time,
                    "message_content": msg.send_message,
                })
            content["chat_list"].append(chat_with_friend)
        
        return render(request, "friendschat/chat_app.html", content)
    else:
        return render(request, "friendschat/chat_error.html", 
            {"error_code": "400", "error_msg": "You made a bad request!"})

@login_required
def chat_logout(request):
    """Logout the user and return to the login page"""
    logout(request)
    return redirect(reverse("login"))

@login_required
def get_message_batch(request, user1: ChatUser, user2: ChatUser, batch_id: int):
    """Get messages between two users
    
    Every batch is 10 messages. 
    batch_id: starts from 0.
    messages range: [batch_id * 10, batch_id * 10 + 10)
    """
    message_key_1 = str(user1.related_user.id) + "_" + str(user2.related_user.id)
    message_key_2 = str(user2.related_user.id) + "_" + str(user1.related_user.id)
    messages = list(ChatMessage.objects.filter(
        message_key__in=[message_key_1, message_key_2]).order_by("-send_time")[batch_id * 10: batch_id * 10 + 10])
    return messages

def _get_google_user(user: User):
    """Try to get the google user which is ChatUser of a user"""
    chat_user = None
    try:
        chat_user = ChatUser.objects.get(related_user=user)
    except ChatUser.DoesNotExist:
        pass
    except ChatUser.MultipleObjectsReturned:
        pass
    return chat_user

@login_required
def get_request_page(request):
    """Retrieve the friends request page"""
    chat_user = _get_google_user(request.user) # Get the current user
    if chat_user is None:
        return render(request, "friendschat/chat_error.html",
            {"error_code": "404", "error_msg": "Related Google user not found!"})
    if request.method == "GET":
        content = {"requests": []}
        for f_request in chat_user.requests.all():
            request_from = f_request.request_from
            content["requests"].append({
                "user_id": request_from.related_user.id,
                "user_pic": request_from.google_pic,
                "user_name": request_from.get_user_name(),
                "user_email": request_from.email,
            })
        return render(request, "friendschat/chat_request.html", content)
    else:
        return render(request, "friendschat/chat_error.html", 
            {"error_code": "400", "error_msg": "You made a bad request!"})

def _error_message_json_response(message: str, status=400):
    """Transfer error message into httpresponse"""
    error_response = {
        "message": message,
    }
    return JsonResponse(error_response, status=status)

def _check_request_user(request_for: ChatUser, self_user: ChatUser) -> bool:
    """Check whether has sent request or been friend"""
    if self_user.friends.contains(request_for):
        return True
    if FriendRequest.objects.filter(request_for=request_for, request_from=self_user).exists():
        return True
    return False

@login_required
@ensure_csrf_cookie
def search_for(request):
    """Send request to request for adding someone"""
    if request.method == "POST":
        if not "email" in request.POST:
            return _error_message_json_response("You are not inputing any email!", 400)
        user_email = request.POST["email"]
        request_user = None
        try:
            request_user = ChatUser.objects.get(email=user_email)
        except ChatUser.DoesNotExist:
            return _error_message_json_response("The user you are searching is not registered!", 404)
        # Check for whether has already sent request or already friend
        chat_user = _get_google_user(request.user)
        if chat_user is None:
            return _error_message_json_response("You are not an authenticated user", 401)
        response_content = {
            "user_id": request_user.related_user.id,
            "user_desc": request_user.description,
            "user_name": request_user.get_user_name(),
            "user_pic": request_user.google_pic,
            "disable": _check_request_user(request_user, chat_user),
        }
        response_json = json.dumps(response_content)
        return HttpResponse(response_json, content_type="application/json")
    else:
        return _error_message_json_response("You are sending incorrect request!", 400)

@login_required
@ensure_csrf_cookie
def send_adding_friend(request):
    """handle adding friend request"""
    if request.method == "POST":
        if not "user_id" in request.POST:
            return _error_message_json_response("You are not sending the user ID", 400)
        target_user_id = None
        try:
            target_user_id = int(request.POST["user_id"])
        except ValueError:
            return _error_message_json_response("You are sending invalid parameter", 400)
        except:
            return _error_message_json_response("You are sending invalid parameter", 400)
        # Check self_chat_user
        self_chat_user = _get_google_user(request.user)
        if self_chat_user is None:
            return _error_message_json_response("You are not an authenticated user", 401)
        # Check other chat_user
        other_chat_user = None
        try:
            other_chat_user = User.objects.get(id=target_user_id)
            other_chat_user = _get_google_user(other_chat_user)
            if other_chat_user is None:
                return _error_message_json_response("The user you are requesting is not existed", 404)
        except:
            return _error_message_json_response("The user you are requesting is not existed", 404)
        # Check whether has added or not
        if not _check_request_user(other_chat_user, self_chat_user):
            # Send the request into
            new_request = FriendRequest(
                request_for=other_chat_user, 
                request_from=self_chat_user, 
                request_time=timezone.now())
            new_request.save()
        
        return JsonResponse({})
    else:
        return _error_message_json_response("You are sending incorrect request!", 400)

@login_required
@ensure_csrf_cookie
def accept_friend(request):
    """THis function will accept the friend request from some friend"""
    if request.method == "POST":
        if not "user_id" in request.POST:
            return _error_message_json_response("You are not specifying the user ID", 400)
        req_user_id = None
        try:
            req_user_id = int(request.POST["user_id"])
        except ValueError:
            return _error_message_json_response("You are sending invalid parameter", 400)
        except:
            return _error_message_json_response("You are sending invalid parameter", 400)
        # Check self_chat_user
        self_chat_user = _get_google_user(request.user)
        if self_chat_user is None:
            return _error_message_json_response("You are not an authenticated user", 401)
        # Check other chat_user
        other_chat_user = None
        try:
            other_chat_user = User.objects.get(id=req_user_id)
            other_chat_user = _get_google_user(other_chat_user)
            if other_chat_user is None:
                return _error_message_json_response("The user you are requesting is not existed", 404)
        except:
            return _error_message_json_response("The user you are requesting is not existed", 404)
        # Check whether has been friend
        if self_chat_user.friends.contains(other_chat_user):
            return JsonResponse({})
        this_request = None
        try:
            this_request = FriendRequest.objects.get(request_for=self_chat_user, 
                request_from=other_chat_user)
        except FriendRequest.DoesNotExist:
            return _error_message_json_response("You are not authorized to accpet this user!", 400)
        except FriendRequest.MultipleObjectsReturned:
            # Delete duplicated requests and accept one
            pass
        # Accept, delete the request and add friend to each other
        FriendRequest.objects.filter(request_for=self_chat_user, 
                request_from=other_chat_user).delete()
        self_chat_user.friends.add(other_chat_user)
        other_chat_user.friends.add(self_chat_user)
        return JsonResponse({})
    else:
        return _error_message_json_response("You are sending incorrect request!", 400)
                 
        

