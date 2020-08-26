from django import forms
from .models import Post, Report, Comment, TutorSession
from django.forms import ModelChoiceField
from tempus_dominus.widgets import DateTimePicker, TimePicker

class AccuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['join_tutee', 'content']

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'placeholder': '예) MySQL 설치하는데 자꾸 오류가 떠요', 'minlength': '15'}))
    class Meta:
        model = Post
        fields = ['title']

class TutorReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['join_tutee', 'content', 'duration_time']

    def __init__(self, *args, **kwargs):
        super(TutorReportForm, self).__init__(*args, **kwargs)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['content', 'duration_time']

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class AcceptReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('content',)


class TutorSessionForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=DateTimePicker(),
    )
    expected_fin_time = forms.DateTimeField(
        widget=DateTimePicker(),
    )
    class Meta:
        model = TutorSession
        fields = ('title', 'session_type', 'location', 'start_time', 'expected_fin_time')
