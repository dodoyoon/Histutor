from django import forms
from .models import Post, Topic
from django.forms import ModelChoiceField

class PostForm(forms.ModelForm):
    topic = forms.ModelChoiceField(queryset=Topic.objects.all().values_list('name', flat=True))

    class Meta:
        model = Post
        fields = ('topic', 'title', 'content')

    # def __init__(self, *args, **kwargs):
    #     super(PostForm, self).__init__(*args, **kwargs)
    #     self.fields['topic']=forms.ModelChoiceField(queryset=Topic.objects.all())
