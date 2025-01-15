from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, BoardCategory
from .forms import PostForm, BoardCategoryForm
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

def post_list(request, category_id=None):
    if category_id:
        category = get_object_or_404(BoardCategory, id=category_id)
        posts = Post.objects.filter(category=category).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')
    return render(request, 'board/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    post.views += 1
    post.save()
    return render(request, 'board/post_detail.html', {'post': post})

def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        category_id = request.POST.get('category')  # 선택된 카테고리 ID 가져오기
        if form.is_valid() and category_id:
            category = get_object_or_404(BoardCategory, id=category_id)  # 카테고리 객체 가져오기
            post = form.save(commit=False)
            post.category = category  # 카테고리 설정
            post.author = request.user  # 작성자 설정
            post.save()
            return redirect('post_list_by_category', category_id=category.id)  # 해당 카테고리 목록으로 이동
    else:
        form = PostForm()
    
    categories = BoardCategory.objects.all()  # 모든 카테고리 가져오기
    return render(request, 'board/post_form.html', {'form': form, 'categories': categories, 'action': '등록'})

def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_list')  # 수정 후 목록으로 이동
    else:
        form = PostForm(instance=post)
    return render(request, 'board/post_form.html', {'form': form, 'action': '수정'})

def post_delete(request, pk):
    if request.method == "POST" and request.is_ajax():
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return JsonResponse({'message': '게시글이 삭제되었습니다.'})
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

def post_list_by_category(request, category_id):
    category = get_object_or_404(BoardCategory, id=category_id)
    
    posts = Post.objects.filter(category=category).order_by('id')
    return render(request, 'board/post_list.html', {'posts': posts, 'category': category})

def category_list(request):
    # 카테고리 쿼리셋 정의 (ID 오름차순으로 정렬)
    categories = BoardCategory.objects.all().order_by('id')

    # 페이지네이션 설정 (페이지당 10개)
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')  # 현재 페이지 번호 가져오기
    page_obj = paginator.get_page(page_number)

    # 템플릿에 데이터 전달
    return render(request, 'board/category_list.html', {
        'page_obj': page_obj,  # 페이지네이션 객체
    })

def category_create(request):
    if request.method == 'POST':
        form = BoardCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # 카테고리 목록으로 리디렉션
    else:
        form = BoardCategoryForm()
    return render(request, 'board/category_form.html', {'form': form, 'action': '등록'})

def category_update(request, pk):
    category = get_object_or_404(BoardCategory, pk=pk)
    if request.method == 'POST':
        form = BoardCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = BoardCategoryForm(instance=category)
    return render(request, 'board/category_form.html', {'form': form, 'action': '수정'})

@csrf_exempt
def category_delete(request, pk):
    print(f"Received request: {request.method}, {request.headers}, PK: {pk}")
    if request.method == 'POST':
        try:
            category = get_object_or_404(BoardCategory, pk=pk)
            category.delete()
            print(f"Category {pk} deleted successfully.")
            return JsonResponse({'message': '카테고리가 삭제되었습니다.'}, status=200)
        except Exception as e:
            print(f"Error deleting category {pk}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    print("Invalid request.")
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)