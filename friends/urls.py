"""friends URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from friendschat import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.chat_board, name='chatboard'),
    path('login', views.chat_login, name='login'),
    path('logout', views.chat_logout, name='logout'),
    path('request_page', views.get_request_page, name='request_page'),
    path('search_user', views.search_for, name='search_user'),
    path('send_adding_friend', views.send_adding_friend, name='send_adding_friend'),
    path('accept_friend', views.accept_friend, name='accept_friend'),
]
