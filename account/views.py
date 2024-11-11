from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account.forms import UserRegistrationForm, UserEditForm
from bot.models import Customer, Telebot
from gift.models import GiftItem
from jdatetime import datetime
from django.db.models import Sum


def count_created_today():
    now = datetime.now()

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    count = Customer.objects.filter(created__range=(start_of_day, end_of_day)).count()
    return count


def get_total_download_count():
    total_downloads = GiftItem.objects.aggregate(total=Sum('download_count'))['total']
    return total_downloads if total_downloads is not None else 0



# Create your views here.
@login_required
def dashboard(request):
    gift_count = GiftItem.objects.count()
    users_count = Customer.objects.count()
    today_users_count = count_created_today()
    total_gift_download = get_total_download_count()
    bot = Telebot.objects.first()

    context = {
        'gift_count':gift_count,
        'users_count':users_count,
        'today_users_count':today_users_count,
        'total_gift_download':total_gift_download,
        'section': 'dashboard'
    }

    if bot:
        context['bot'] = bot

    return render(
        request,
        'account/dashboard.html',
        context
    )

@login_required
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile updated '\
                                      'successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
    return render(
        request,
        'account/edit.html',
        {'user_form': user_form,}
    )