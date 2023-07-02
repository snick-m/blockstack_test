from django.shortcuts import render, redirect, get_object_or_404

from .models import Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from feed.models import Post

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.forms.models import model_to_dict

from django.conf import settings
from django.http import HttpResponseRedirect

from django.contrib.auth import logout

import random

# Create your views here.

"""
register
login
logout

profile
edit_profile

users_list
friends_list

send_invite
accept_invite

disconnect
"""

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        print(form.errors)
        if form.is_valid():
            user = form.save()
            user.save()
            return redirect("register")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("/")


@login_required
def profile(request, username=""):
    profile = get_object_or_404(
        Profile, user=(username if username != "" else request.user)
    )
    return render(request, "users/profile.html", {"profile": profile})


@login_required
def users_list(request):
    user = Profile.objects.get(user=request.user)
    sent_invites = list(user.sent_invites.values_list("receiver", flat=True))
    friends = list(user.friends.all())

    suggestions = []

    for u in friends:
        uFriends = (
            u.friends.all()
            .exclude(user=request.user)
            .exclude(user__in=friends)
            .exclude(user__in=sent_invites)
        )
        for f in uFriends:
            if f not in friends and f not in sent_invites and f != user:
                suggestions.append(f)

    if len(suggestions) < 10:
        remaining_count = 10 - len(suggestions)
        unknowns = list(
            Profile.objects.exclude(user=request.user)
            .exclude(user__in=friends)
            .exclude(user__in=sent_invites)[: 20 - len(suggestions)]
        )
        if len(unknowns) > remaining_count:
            unknowns = random.sample(list(unknowns), remaining_count)
        suggestions += list(unknowns)

    return render(request, "users/users_list.html", {"suggestions": suggestions})


@login_required
def profile(request, username):
    user_profile = Profile.objects.get(user=request.user)
    target_profile = get_object_or_404(Profile, user=username)

    context = {
        "friends": list(user_profile.friends.all()),
        "sent_invites": list(
            user_profile.sent_invites.values_list("receiver", flat=True)
        ),
        "received_invites": list(user_profile.invites.values_list("sender", flat=True)),
        "profile": target_profile,
        "user": request.user,
        "posts": target_profile.posts.all().order_by("-date_posted"),
    }

    return render(
        request,
        "users/profile.html",
        context,
    )


@login_required
def self_profile(request):
    return profile(request, request.user.username)


@login_required
def invite(request, username, operation="create"):
    user = Profile.objects.get(user=request.user)
    invitee = Profile.objects.get(user=username)

    if invitee in user.friends.all():
        return redirect("/profile/" + username)

    if operation == "create":
        if invitee.user.username in user.sent_invites.values_list(
            "receiver", flat=True
        ):
            return redirect("/profile/" + username)

        invite = user.sent_invites.create(
            sender=user.user.username, receiver=invitee.user.username
        )

        invitee.invites.add(invite)
        invite.save()

    if operation == "delete":
        if invitee.user.username not in user.sent_invites.values_list(
            "receiver", flat=True
        ):
            return redirect("/profile/" + username)

        invite = user.sent_invites.get(
            sender=user.user.username, receiver=invitee.user.username
        )

        invitee.invites.remove(invite)
        user.sent_invites.remove(invite)

        invite.delete()

    if operation == "accept":
        if invitee.user.username not in user.invites.values_list("sender", flat=True):
            return redirect("/profile/" + username)

        invite = user.invites.get(
            sender=invitee.user.username, receiver=user.user.username
        )
        invite.accepted = True
        invite.save()

        user.friends.add(invitee)
        invitee.friends.add(user)

        user.invites.remove(invite)
        invitee.sent_invites.remove(invite)

        invite.delete()

    invitee.save()
    user.save()

    return redirect("/profile/" + username)


@login_required
def disconnect(request, username):
    user = Profile.objects.get(user=request.user)
    friend = Profile.objects.get(user=username)

    if friend not in user.friends.all():
        return redirect("/profile/" + username)

    user.friends.remove(friend)
    friend.friends.remove(user)

    user.save()
    friend.save()

    return redirect("/profile/" + username)


@login_required
def edit_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=Profile.objects.get(user=request.user)
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account has been updated!")
            return redirect("/profile")

        print(u_form.errors, p_form.errors)
    else:
        p = Profile.objects.get(user=request.user)
        u_form = UserUpdateForm(
            model_to_dict(p.user, fields=["first_name", "last_name", "email"]),
            instance=request.user,
        )
        p_form = ProfileUpdateForm(
            model_to_dict(p, fields=["bio", "birthdate"]), instance=p
        )

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "profile": get_object_or_404(Profile, user=request.user),
    }

    return render(request, "users/edit_profile.html", context)
