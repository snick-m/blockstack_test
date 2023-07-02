from djongo import models

# Create your models here.
class Post(models.Model):
    _id = models.ObjectIdField()
    author = models.ForeignKey('users.Profile', to_field="user", on_delete=models.CASCADE, related_name='author')
    body = models.TextField(max_length=500)
    date_posted = models.DateTimeField(auto_now_add=True)
    likes = models.ArrayReferenceField(to='users.Profile', to_field="user", on_delete=models.CASCADE, blank=True, null=True)
    comments = models.ArrayReferenceField(to='self', on_delete=models.CASCADE, blank=True, null=True, related_name='comment')
    is_comment = models.BooleanField(default=False, null=False)
    shared = models.BooleanField(default=False)
    original_post = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.author.user.first_name} posted on {self.date_posted}.'