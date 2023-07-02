from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import PostCreateForm
from .models import Post
from users.models import Profile

from bson.objectid import ObjectId

from django.utils import timezone
from bson import json_util

from django.forms.models import model_to_dict

# Create your views here.


@login_required
def home(request: HttpRequest):
    allowed_authors = list(request.user.profile.friends.all())
    allowed_authors.append(request.user.profile)
    feed_posts = (
        Post.objects.filter(author__in=allowed_authors)
        .filter(is_comment__in=[False, None])
        .order_by("-date_posted")
    )[:10]

    for post in feed_posts:
        post.comments = post.comments.order_by("-date_posted")

    return render(
        request,
        "feed/home.html",
        {
            "feed_posts": feed_posts,
        },
    )


def index(request: HttpRequest):
    print(request.user.is_authenticated)
    return redirect("home" if request.user.is_authenticated else "login")


@login_required
def post(request: HttpRequest, post_id: ObjectId):
    post = get_object_or_404(Post, _id=ObjectId(post_id))
    return render(request, "feed/post.html", {"post": post})

@login_required
def create_post(request: HttpRequest):
    if request.method == "POST":
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.profile
            post.date_posted = timezone.now()
            post.save()
            return redirect("home")
    else:
        form = PostCreateForm()

    return render(request, "feed/create_post.html", {"form": form})


@login_required
def like_post(request: HttpRequest, post_id: ObjectId):
    post = get_object_or_404(Post, _id=ObjectId(post_id))
    if request.user.profile not in post.likes.all():
        post.likes.add(request.user.profile)
    else:
        post.likes.remove(request.user.profile)
    post.save()

    return HttpResponse(
        json_util.dumps(
            {
                "post_id": post_id,
                "liked": request.user.profile in post.likes.all(),
                "likes": len(post.likes.all()),
            }
        ),
        content_type="application/json",
    )


@login_required
def comment_post(request: HttpRequest, post_id: ObjectId):
    post = get_object_or_404(Post, _id=ObjectId(post_id))
    form = PostCreateForm(request.POST)

    # print(request.POST.body)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user.profile
        comment.date_posted = timezone.now()
        comment.is_comment = True
        comment.save()
        post.comments.add(comment)
        post.save()
        post.comments = post.comments.order_by("-date_posted")
        return render(request, "feed/post.html", {"post": post})

    return HttpResponse(
        json_util.dumps(
            {
                "post_id": post_id,
                "comment": None,
            }
        ),
        content_type="application/json",
    )
