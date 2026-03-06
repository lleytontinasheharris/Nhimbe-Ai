"""Forum forms - Post and Comment creation"""

from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Form for creating and editing forum posts"""

    class Meta:
        model = Post
        fields = ['title', 'category', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'What would you like to discuss?'
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-input'
        })
        self.fields['content'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Share your thoughts, questions, or experiences...',
            'rows': 8
        })


class CommentForm(forms.ModelForm):
    """Form for adding comments to posts"""

    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Share your thoughts...',
            'rows': 4
        })
        self.fields['content'].label = ''