from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def main_home(request):
    return render(request, 'shop/main_home.html')

def home(request):
    return HttpResponse("<h1>Welcome to My Shop!</h1><p>This is my custom page.</p>")