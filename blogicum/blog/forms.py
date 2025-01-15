from django import forms
from django.utils import timezone

from .models import Comment, Post


class CreatePostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        initial=timezone.now,
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
            },
            format='%Y-%m-%dT%H:%M',
        ),
    )

    class Meta:
        model = Post
        exclude = ('author',)


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(CreateCommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = forms.Textarea(attrs={
            'rows': 4,
            'cols': 35,
            'placeholder': 'Введите ваш комментарий...',
        })
