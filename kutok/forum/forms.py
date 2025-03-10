from django import forms
from .models import Thread, Comment


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content', 'category', 'country']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введіть назву обговорення'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Текст обговорення'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
        }


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='Ваш коментар',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Напишіть ваш коментар...'
        })
    )

    class Meta:
        model = Comment
        fields = ('content',)