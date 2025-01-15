from .models import Product

def recently_viewed_products(request):
    """
    Retrieve recently viewed products from cookies.
    """
    recently_viewed = request.COOKIES.get('recently_viewed', '')
    if recently_viewed:
        product_ids = recently_viewed.split(',')
        products = Product.objects.filter(id__in=product_ids)
        return sorted(products, key=lambda p: product_ids.index(str(p.id)))
    return []