from djongo import models
from django.core.validators import URLValidator, EmailValidator

from django.db.models.signals import post_save
from django.conf import settings

from feed.models import Post


# Create your models here.
class Link(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(validators=[URLValidator])

    class Meta:
        abstract = True


class Invite(models.Model):
    _id = models.ObjectIdField(primary_key=True, unique=True, editable=False)
    sender = models.CharField(max_length=50, blank=False, null=False)
    receiver = models.CharField(max_length=50, blank=False, null=False)
    accepted = models.BooleanField(default=False)

    # class Meta:


class Profile(models.Model):
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, to_field="username", primary_key=True
    )

    birthdate = models.DateField(blank=False, null=False, default="2000-01-01")

    image = models.ImageField(
        default="default.jpg", upload_to="profile_pics", blank=True, null=True
    )
    friends = models.ArrayReferenceField(to="self", to_field="user", blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    links = models.ArrayField(
        model_container=Link, blank=True
    )  # Array of links to other social media

    invites = models.ArrayReferenceField(
        to=Invite,
        blank=True,
        null=True,
        related_name="received_invites",
    )  # Received invites
    sent_invites = models.ArrayReferenceField(
        to=Invite,
        blank=True,
        null=True,
        related_name="sent_invites",
    )  # Sent invites

    # Shared posts will have a reference to the original post and a blank body
    posts = models.ArrayReferenceField(to="feed.Post", to_field="_id", blank=True, null=True)


def post_save_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Profile.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
            ).save()
        except Exception as e:
            print(e)
            pass


def create_post_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            p = Profile.objects.get(user=instance.author)
            p.posts.add(instance)
            p.save()
        except Exception as e:
            print(e)
            pass


post_save.connect(post_save_user_model_receiver, sender=settings.AUTH_USER_MODEL)
post_save.connect(create_post_user_model_receiver, sender=Post)
