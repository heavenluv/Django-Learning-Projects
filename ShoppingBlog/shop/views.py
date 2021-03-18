from django.shortcuts import get_object_or_404, render
from .models import Category, Product
from cart.forms import CartAddProductForm
# Create your views here.

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)
    content = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request,'shop/product/list.html',content)

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    content = {
        'product':product,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'shop/product/detail.html', content)