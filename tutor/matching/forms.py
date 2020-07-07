from django import forms
<<<<<<< HEAD
from .models import Post, Topic, Report
=======
from .models import Post, Topic, User
>>>>>>> 8fc4fb73b74c49c4d3543be6aec6020600369c14
from django.forms import ModelChoiceField

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'student_number','nickname', 'phone', 'email'] 

class PostForm(forms.ModelForm):
    topic = forms.ModelChoiceField(queryset=Topic.objects.all().values_list('name', flat=True))

    class Meta:
        model = Post
        fields = ('topic', 'title', 'content')

<<<<<<< HEAD
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['topic']=forms.ModelChoiceField(queryset=Topic.objects.all())

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('meeting_date','meeting_duration_time','content')
=======
    # def __init__(self, *args, **kwargs):
    #     super(PostForm, self).__init__(*args, **kwargs)
    #     self.fields['topic']=forms.ModelChoiceField(queryset=Topic.objects.all())
>>>>>>> 8fc4fb73b74c49c4d3543be6aec6020600369c14
