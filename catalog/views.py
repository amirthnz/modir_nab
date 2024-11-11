from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Product, Category
from catalog.forms import CategoryForm, ProductForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# List categories
def list_category(request):
    categories = Category.objects.all()
    return render(request, 'catalog/categories/list.html', {'categories': categories})


# Add category using form
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalog:cat_list')


    form = CategoryForm()
    return render(request, 'catalog/categories/add.html', {'form': form})


# Edit category using form
def edit_category(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('catalog:cat_list')

    form = CategoryForm(instance=category)
    return render(request, 'catalog/categories/edit.html', {'form': form})


# Delete category
def delete_category(request, pk):
    category = get_object_or_404(Category, id=pk)
    category.delete()
    return redirect('catalog:cat_list')


# list all products
def list_product(request):
    product_list = Product.objects.all()
    # Pagination with 12 people per page
    paginator = Paginator(product_list, 12)
    page_number = request.GET.get('page', 1)
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        products = paginator.page(paginator.num_pages)
    return render(request, 'catalog/products/list.html', {'products': products})


# Add product using form
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog:product_list')


    form = ProductForm()
    return render(request, 'catalog/products/add.html', {'form': form})


# Edit product using form
def edit_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('catalog:product_list')

    form = ProductForm(instance=product)
    return render(request, 'catalog/products/edit.html', {'form': form})



# Delete product
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    product.delete()
    return redirect('catalog:product_list')