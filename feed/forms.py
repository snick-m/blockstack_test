from django import forms
from crispy_forms import helper, layout

from django.contrib.auth.models import User

from users.models import Profile

from .models import Post


class PostCreateForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Post
        fields = ['body']
    
    def __init__(self, *args, **kwargs):
        super(PostCreateForm, self).__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(layout.Submit('submit', 'Post'))
        self.helper.layout = layout.Layout(
            layout.Fieldset(
                'Create Post',
                'body',
            )
        )