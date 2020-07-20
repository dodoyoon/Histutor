from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt 
from webpush import send_user_notification
import json

@require_GET # GET response에만 이 뷰가 실행되도록 함
def home(request):
    return HttpResponse('<h1>Home Page<h1>')

'''
It will be restricted to POST requests only and will be exempted from Cross Site Request Forgery (CSRF) protection. 
Doing this will allow you to test the view using Postman or any other RESTful service. 
In production, however, you should remove this decorator to avoid leaving your views vulnerable to CSRF.
'''

@require_POST # POST request에만 이 뷰가 실행되도록 함
@csrf_exempt  # CSRF protection을 벗어나서 이 뷰가 실행될 수 있도록 함.
def send_push(request):
    try:
        body = request.body
        data = json.loads(body)
        '''
        json.loads  : JSON document를 ㅂ다아서 python object를 바꿔줌
        '''

        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message" : "Invalid data format"})
        
        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {'head': data['head'], 'body': data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)
        '''
        head: The title of the push notification.
        body: The body of the notification.
        id: The id of the request user.
        '''
        return JsonResponse(status=200, data={"message" : "web push successful"})
    except TypeError:
        return JsonResponse(status=500, data={"message" : "An error occurred"})
