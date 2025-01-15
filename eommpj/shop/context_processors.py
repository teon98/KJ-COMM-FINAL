from .utils import recently_viewed_products

def recently_viewed_context(request):
    """
    Add recently viewed products to the template context.
    """
    return {
        'recently_viewed_products': recently_viewed_products(request),
    }
