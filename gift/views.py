from django.shortcuts import render, redirect
from gift.models import GiftItem
from gift.forms import GiftForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required
def gift_list(request):
    gifts = GiftItem.objects.all()

    context = {
        'section':'gifts',
        'gifts':gifts
    }

    return render(request, 'gift/gift_list.html', context)

@login_required
def gift_add(request):
    if request.method == 'POST':
        form = GiftForm(request.POST, request.FILES)
        if form.is_valid():
            gift = form.save()
            messages.success(request, 'هدیه با موفقیت افزوده شد، می توانید آن را ویرایش کنید:')
            return redirect('gift:edit_gift', gift.id)
        else:
            messages.error(request, 'اشکالی در افزوده هدیه بوجود آمد...لطفا دوباره تلاش کنید')
    else:
        form = GiftForm()
    context = {
        'form':form,
    }

    return render(request, 'gift/gift_add.html', context)

@login_required
def gift_detail(request, id):
    gift = GiftItem.objects.get(id=id)
    if request.method == 'POST':
        form = GiftForm(request.POST, request.FILES, instance=gift)
        if form.is_valid():
            form.save()
            return redirect('gift:gift_list')
    else:
        form = GiftForm(instance=gift)
    context = {
        'form':form,
        'gift':gift
    }

    return render(request, 'gift/gift_detail.html', context)


@login_required
def gift_delete(request, id):
    gift = GiftItem.objects.get(id=id)
    if request.method == 'POST':
        gift.delete()
        return redirect('gift:gift_list')