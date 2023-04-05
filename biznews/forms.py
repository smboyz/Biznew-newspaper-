from django import forms
from biznews.models import NewsLetter, Contact, Comment, Post, Category, Tag

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "featured_image", "status", "category", "tag")

class NewsLetterForm(forms.ModelForm):
    class Meta:
        model = NewsLetter
        fields = "__all__"

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__" 

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__" 

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"         