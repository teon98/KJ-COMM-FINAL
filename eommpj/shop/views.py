from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from .models import Post
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
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
    fields = ['title','content','head_image','file_upload','price']

    def form_valid(self, form):
        # 저장 후, 'post_list' 페이지로 리디렉션
        post = form.save()
        return redirect('post_list')  # 'post_list' URL로 리디렉션
    
class PostDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')  # 삭제 후 이동할 URL

    def get(self, request, *args, **kwargs):
        """
        GET 요청이 오더라도 바로 삭제를 처리하고 success_url로 리디렉션.
        """
        return self.post(request, *args, **kwargs)
    
class PostUpdate(UpdateView):
    model = Post
    fields = ['title','content','head_image','file_upload','price']

    template_name = 'shop/post_update_form.html'
    success_url = reverse_lazy('post_detail')  # 수정 후 이동할 페이지, pk를 사용한 URL로 변경 가능

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})