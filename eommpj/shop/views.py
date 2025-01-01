from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from .models import Post
from django.views.generic import ListView, DetailView
# from .serializer import BlogSerializer

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.http import Http404

# Create your views here.

def main_home(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')  # 로그인 후 홈 화면으로 리디렉션
    else:
        form = AuthenticationForm()
    return render(request, 'main_home.html', {'form': form})

class PostList(ListView):
    model = Post
    ordering = '-pk'

class PostDetail(DetailView):
    model = Post

class PostCreate(CreateView):
    model = Post
    fields = ['title','content','head_image','file_upload']