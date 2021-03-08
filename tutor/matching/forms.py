from django import forms
from .models import Post, Report, Comment, TutorSession, TutorApplication
from django.forms import ModelChoiceField
from tempus_dominus.widgets import DateTimePicker, TimePicker
import datetime
from datetime import timedelta

class AccuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['join_tutee', 'content']

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'placeholder': '예) OS에 Deadlock에 대해서 도움이 필요합니다.', 'minlength': '15', 'maxlength': '70'}))
    class Meta:
        model = Post
        fields = ['title']

class TutorReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'cols':28, 'rows':14, 'required':True,'maxlength':1000, 'autofocus':True}),
        }

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

    def __init__(self, *args, **kwargs):
        super(TutorSessionForm, self).__init__(*args, **kwargs)
        now = datetime.datetime.now()
        
        if int('{%M}'.format(now)) > 10:
            now += timedelta(hours=1)
            
        later_time = now + timedelta(hours=1)
        
        start_time_str = '{%Y-%M-%D %H:00:00}'.format(now)
        end_time_str = '{%Y-%M-%D %H:00:00}'.format(later_time)

        self.fields['start_time'].widget = DateTimePicker(
            options={
                'defaultDate': start_time_str,
                'vertical': 'top',
            }
        )

        self.fields['expected_fin_time'].widget = DateTimePicker(
            options={
                'defaultDate': end_time_str,
                'vertical': 'top',
            }
        )


class TutorApplicationForm(forms.ModelForm):
    content = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '신청 이유를 간단하게 적어주세요.'}))
    class Meta:
        model = TutorApplication
        fields = ('content',)
