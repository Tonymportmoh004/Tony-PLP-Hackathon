from django import forms
from .models import CustomUser, blogPost, Comment

class CustomUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'id': 'username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id': 'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'password'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'id': 'bio'}))
    location = forms.CharField(widget=forms.TextInput(attrs={'id': 'location'}))
    profile_pic = forms.ImageField(widget=forms.FileInput(attrs={'id': 'profile_pic'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'bio', 'location', 'profile_pic']

class blogPostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'id': 'title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'id': 'content'}))
    author = forms.ModelChoiceField(queryset=CustomUser.objects.all(), widget=forms.Select(attrs={'id': 'author'}))

    class Meta:
        model = blogPost
        fields = ['title', 'content', 'author']

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'id': 'content'}))
    author = forms.ModelChoiceField(queryset=CustomUser.objects.all(), widget=forms.Select(attrs={'id': 'author'}))
    post = forms.ModelChoiceField(queryset=blogPost.objects.all(), widget=forms.Select(attrs={'id': 'post'}))

    class Meta:
        model = Comment
        fields = ['content', 'author', 'post']
