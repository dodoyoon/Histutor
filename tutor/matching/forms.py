from django import forms
from .models import Post, Report, Profile, Comment
from django.forms import ModelChoiceField

class AccuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['tutee_feedback']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname']
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # add custom error messages
        self.fields['nickname'].error_messages.update({
            'required': '닉네임을 입력하세요',
        })

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title']

class DateInput(forms.DateInput):
    input_type = 'date'



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class AcceptReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('tutee_feedback',)
