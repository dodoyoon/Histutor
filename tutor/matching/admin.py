from django.contrib import admin
from .models import Profile, Post, Comment, Report, TutorSession, SessionLog
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Report)
admin.site.register(TutorSession)
admin.site.register(SessionLog)

