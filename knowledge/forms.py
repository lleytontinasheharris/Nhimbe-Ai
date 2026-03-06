"""Knowledge Base forms"""

from django import forms
from .models import Article, ArticleCategory


class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles"""
    
    # Radio choice for author type
    AUTHOR_TYPE_CHOICES = [
        ('self', 'I wrote this article'),
        ('external', 'External source (FAO, AGRITEX, etc.)'),
    ]
    
    author_type = forms.ChoiceField(
        choices=AUTHOR_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='self',
        label="Who wrote this article?"
    )

    class Meta:
        model = Article
        fields = [
            'title', 'category', 'difficulty', 'summary', 'content',
            'external_author', 'source_name', 'source_url',
            'featured_image', 'downloadable_file', 'file_description',
            'is_published', 'is_featured'
        ]
        widgets = {
            'summary': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Brief description that appears in article listings...'
            }),
            'content': forms.Textarea(attrs={
                'rows': 20,
                'placeholder': 'Write your article content here. You can use HTML tags like <h2>, <p>, <ul>, <li>, <strong>...'
            }),
            'external_author': forms.TextInput(attrs={
                'placeholder': 'e.g., Dr. John Moyo, FAO Zimbabwe, AGRITEX'
            }),
            'source_name': forms.TextInput(attrs={
                'placeholder': 'e.g., FAO Publications, Zimbabwe Farmer Magazine'
            }),
            'source_url': forms.URLInput(attrs={
                'placeholder': 'https://...'
            }),
            'file_description': forms.TextInput(attrs={
                'placeholder': 'e.g., Complete Guide (PDF, 2.5MB)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        author_type = cleaned_data.get('author_type')
        external_author = cleaned_data.get('external_author')

        if author_type == 'external' and not external_author:
            self.add_error('external_author', 'Please provide the external author or organization name.')

        return cleaned_data