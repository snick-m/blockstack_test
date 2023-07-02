"""
URL configuration for blockstack_test project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

from users import views as user_views
from feed import views as feed_views

from users import forms as user_forms

from django.http import request

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", feed_views.index, name="index"),
    path("admin/", admin.site.urls),
    
    path("users/", user_views.users_list, name="users_list"),
    path("register/", user_views.register, name="register"),

    path("profile/", user_views.self_profile, name="profile"),
    path("profile/<username>", user_views.profile, name="profile"),
    path("profile/<username>/invite/<operation>", user_views.invite, name="invite"),
    path("profile/<username>/disconnect/", user_views.disconnect, name="disconnect"),
    path("profile/edit/", user_views.edit_profile, name="edit_profile"),

    path("posts/<post_id>", feed_views.post, name="post"),
    path("posts/<post_id>/like", feed_views.like_post, name="like"),
    path("posts/<post_id>/comment", feed_views.comment_post, name="comment"),
    
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="users/login.html",
            extra_context={"user_login_form": user_forms.UserLoginForm()},
        ),
        name="login",
    ),
    path("logout/", user_views.logout_view, name="logout"),
    
    path("home/", feed_views.home, name="home"),

    path("create_post/", feed_views.create_post, name="create_post"),
]
