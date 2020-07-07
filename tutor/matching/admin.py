from django.contrib import admin
from .models import User, Topic, Post, Comment, Report

admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Report)

# Register your models here.
