from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, BoardCategory
from .forms import PostForm, BoardCategoryForm
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import F

def post_list(request, category_id=None):
    if category_id:
        category = get_object_or_404(BoardCategory, id=category_id)
        posts = Post.objects.filter(category=category).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')
    return render(request, 'board/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    Post.objects.filter(id=pk).update(views=F('views') + 1)
    return render(request, 'board/post_detail.html', {'post': post})

def save_post(request, post=None):
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        category_id = request.POST.get('category')
        if form.is_valid() and category_id:
            category = get_object_or_404(BoardCategory, id=category_id)
            post = form.save(commit=False)
            post.category = category
            post.author = request.user
            post.save()
            return redirect('post_list_by_category', category_id=category.id)
    else:
        form = PostForm(instance=post)
    
    categories = BoardCategory.objects.all()
    action = '수정' if post else '등록'
    return render(request, 'board/post_form.html', {'form': form, 'categories': categories, 'action': action})

def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        category_id = request.POST.get('category')
        if form.is_valid() and category_id:
            category = get_object_or_404(BoardCategory, id=category_id)
            post = form.save(commit=False)
            post.category = category
            post.author = request.user
            #A/S 접수 카테고리일 경우 상태를 '대기'로 설정
            if category.name == "A/S 접수":
                post.status = '대기'
            post.save()
            return redirect('post_list_by_category', category_id=category.id)
    else:
        form = PostForm()
    categories = BoardCategory.objects.all()
    return render(request, 'board/post_form.html', {'form': form, 'categories': categories, 'action': '등록'})

def update_status(request, pk):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=pk)
        new_status = request.POST.get('status')

        if new_status in ['대기', '처리 중', '처리 완료']:
            post.status = new_status
            post.save()
            return JsonResponse({'message': '상태가 업데이트되었습니다.', 'status': post.status})
        else:
            return JsonResponse({'error': '유효하지 않은 상태 값입니다.'}, status=400)
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=405)

def post_update(request, pk):
    # 수정하려는 게시글 가져오기
    post = get_object_or_404(Post, pk=pk)
    print("얍", post)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)  # 기존 인스턴스 전달
        if form.is_valid():
            form.save()  # 수정된 데이터 저장
            return redirect('post_detail', pk=post.pk)  # 상세 페이지로 이동
    else:
        form = PostForm(instance=post)  # 기존 데이터를 포함한 폼 생성
    categories = BoardCategory.objects.all()
    # 템플릿에 폼과 게시글 전달
    return render(request, 'board/post_form.html', {'form': form, 'categories': categories,'post': post, 'action': '수정'})

def post_delete(request, pk):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return JsonResponse({'message': '게시글이 삭제되었습니다.'})
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

def post_list_by_category(request, category_id):
    category = get_object_or_404(BoardCategory, id=category_id)
    posts = Post.objects.filter(category=category).order_by('-created_at')
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