from django.contrib import admin
from .models import User, Post, Comment, Topic, Report
# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Report)
admin.site.register(Comment)
