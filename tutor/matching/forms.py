from django import forms
from .models import Post, Report, Comment, TutorSession, TutorApplication
from django.forms import ModelChoiceField
from tempus_dominus.widgets import DateTimePicker, TimePicker
import datetime

class AccuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['join_tutee', 'content']

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'placeholder': '예) OS에 Deadlock에 대해서 도움이 필요합니다.', 'minlength': '15'}))
    class Meta:
        model = Post
        fields = ['title']

class TutorReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['join_tutee', 'content', 'duration_time']
        widgets = {
            'content': forms.Textarea(attrs={'cols':28, 'rows':8, 'required':True,'maxlength':1000, 'autofocus':True}),
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
        year_info = now.strftime('%Y-%m-%d')
        hour = now.hour
        min = now.minute

        if min > 10:
            hour += 1

        start_time_str = year_info + " " + str(hour) + ':00'
        end_time_str = year_info + " " + str(hour+1) + ':00'

        self.fields['start_time'].widget = DateTimePicker(
            options={
                'defaultDate': start_time_str,
            }
        )

        self.fields['expected_fin_time'].widget = DateTimePicker(
            options={
                'defaultDate': end_time_str,
            }
        )


class TutorApplicationForm(forms.ModelForm):
    content = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '신청 이유를 간단하게 적어주세요.'}))
    class Meta:
        model = TutorApplication
        fields = ('content',)
