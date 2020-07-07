from django.shortcuts import render

def main(request):
    ctx = {}
    
    return render(request, 'tutor/main.html', ctx)