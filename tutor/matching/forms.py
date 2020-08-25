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
        # self.fields['content'].widget.attrs = {
        #     'placeholder': "튜터링 보고서는 운영자 및 담당 교수만 확인 가능합니다",
        # }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class AcceptReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('content',)


class TutorSessionForm(forms.ModelForm):
    # start_time = forms.DateTimeField(
    #     widget=DateTimePicker(),
    # )
    # fin_time = forms.DateTimeField(
    #     widget=DateTimePicker(),
    # )
    class Meta:
        model = TutorSession
        fields = ('title', 'session_type', 'location', 'start_time', 'fin_time')
