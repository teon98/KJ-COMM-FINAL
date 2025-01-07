from shop.models import Category

def categories_context(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    return {'categories': categories}
