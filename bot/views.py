from django.shortcuts import render, redirect
from bot.models import Customer, Telebot, Post
from gift.models import GiftItem
from django.contrib.auth.decorators import login_required
from bot.forms import RobotForm, CustomerForm, PostEditForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from requests.exceptions import ConnectTimeout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from bot.services.telegram_api import TelegramService
import json
from bot import data
import os
from django.conf import settings
import jdatetime
from bot import titles
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import async_to_sync
from notification.models import Notif
from catalog.models import Category, Product
import mimetypes
# import logging

# logger = logging.getLogger('core')


def get_bot_token():
        try:
            bot = Telebot.objects.first()
            return bot.token
        except ObjectDoesNotExist:
            return None


def generate_keyboard(items=None, custom_keyboard = False):
    posts = Post.objects.all()
    post_title = [post.title for post in posts]  # Extract the titles from the Post objects
    new_keyboard = []
    if custom_keyboard:
        new_keyboard = generate_custom_list(items)
    else:
        new_keyboard = generate_item_list(post_title, titles.GET_PERSONAL_ASSISTANCE, titles.RECIEVE_GIFT, titles.CATALOG)
    return new_keyboard

def generate_item_list(items, fixed_item1, fixed_item2, fixed_item3,chunk_size=2):
    # Initialize the result list with the two distinct fixed items
    result = [[fixed_item1, fixed_item2], [fixed_item3]]

    # Loop through the items and group them in chunks of 'chunk_size'
    for i in range(0, len(items), chunk_size):
        result.append(items[i:i + chunk_size])

    return result

def generate_custom_list(items,chunk_size=2):
    # Initialize the result list with the two distinct fixed items
    result = []

    # Loop through the items and group them in chunks of 'chunk_size'
    for i in range(0, len(items), chunk_size):
        result.append(items[i:i + chunk_size])

    result.append([titles.BACK])

    return result


class TelegramWebhookAPI(APIView):
    """
    Handles incoming webhook requests from Telegram
    """

    telegram_service = TelegramService()

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        # Get telegram update object
        data = request.data
        # print(data)
        # message->from->id
        message = data.get('message', {})
        callback_query = data.get('callback_query', {})
        reply_to_message = message.get('reply_to_message', {})
        if message:
            from_user = message.get('from', {})
            chat_id = from_user.get('id')
            text = message.get('text')
            # Process the message
            self.proccess_message(chat_id, from_user, text, message, request, reply_to_message)
        elif callback_query:
            self.handle_callback_query(callback_query)

        # Process update

        return Response({'status', 'ok'}, status=status.HTTP_200_OK)

    def proccess_message(self, chat_id, from_user, text, message, data, reply_to_message={}):
        first_name = from_user.get('first_name', '')
        last_name = from_user.get('last_name', '')
        username = from_user.get('username', '')
        has_username = username != ''
        posts = Post.objects.all()
        categories = Category.objects.all()
        # Process the message
        if reply_to_message:
            reply_to_message_text = reply_to_message.get('text')
            print(reply_to_message_text)
            if reply_to_message_text == titles.GET_PHONE_NUMBER_MESSAGE:
                print('User replyed to phone number request')
                try:
                    user = Customer.objects.get(chat_id=chat_id)
                    contact = message.get('contact', {})
                    phone_number = contact.get('phone_number')
                    if user:
                        user.phone_number = phone_number
                        user.has_phone_number = True
                        user.save()
                        notification = Notif.objects.create(
                            from_user = user,
                            message = 'شماره همراه خود را برای دریافت مشاوره ثبت کرد'
                        )
                        notification.save()

                        reply_markup = {
                            'keyboard': generate_keyboard(),
                            'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
                            'one_time_keyboard': False  # Optional: hide the keyboard after a button press
                        }
                        self.telegram_service.send_message_with_keyboard(chat_id, 'با تشکر، مشاورین ما در اسرع وقت با شما تماس میگیرند', reply_markup)
                except ObjectDoesNotExist:
                    pass


        else:
            if '/start' in text:
                # First time user
                try:
                    user = Customer.objects.get(chat_id=chat_id)
                    # Send welcome back message
                    self.telegram_service.send_welcome_message(chat_id)
                except ObjectDoesNotExist:
                    print("CREATING A NEW USER")
                    # res = self.telegram_service.get_user_profile_photo(chat_id)
                    obj, created = Customer.objects.get_or_create(
                        chat_id=chat_id,
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        defaults={
                            "has_username":has_username,
                            "has_recieved_gift":False,
                            "created":jdatetime.datetime.now(),
                            "modified":jdatetime.datetime.now()
                        }
                    )
                    if created:
                        # res = self.telegram_service.get_user_profile_photo(chat_id)
                        # if res:  # Check if profile picture was saved successfully
                        #     # logger.info(f"Profile picture saved for user {first_name} {last_name} (chat_id: {chat_id})")
                        #     pass
                        self.telegram_service.send_welcome_message(chat_id)


            elif titles.RECIEVE_GIFT in text:
                current_user = Customer.objects.get(chat_id=chat_id)
                if current_user.has_recieved_gift:
                    reply_markup = {
                        'keyboard': generate_keyboard(),
                        'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
                        'one_time_keyboard': False  # Optional: hide the keyboard after a button press
                    }
                    self.telegram_service.send_message_with_keyboard(chat_id, 'شما هدیه خود را دریافت کرده اید\nبرای دریافت هدیه بیشتر به ربات سر بزنید', reply_markup)
                else:
                    self.telegram_service.send_gift_choices(chat_id)
            elif titles.GET_PERSONAL_ASSISTANCE in text:     # User wants to get personal assistance
                try:
                    user = Customer.objects.get(chat_id=chat_id)
                    if user:
                        if user.has_phone_number:
                            self.telegram_service.send_telegram_message(chat_id, 'شماره شما در نوبت انتظار ثبت شده است', False)
                        else:
                            # Here we should send out keyboard with share contact button
                            messageText = titles.GET_PHONE_NUMBER_MESSAGE
                            contactKeyboard = {
                                "keyboard": [[{
                                    "text": "اشتراک گذاری شماره",
                                    "request_contact": True
                                }], [titles.BACK]],
                                "one_time_keyboard": True,
                                "resize_keyboard": True
                            }
                            self.telegram_service.send_message_with_keyboard(chat_id, messageText, contactKeyboard)
                            # self.telegram_service.send_reply_message(chat_id, titles.GET_PHONE_NUMBER_MESSAGE)
                except Exception as e:
                    print(e)
                        # User has not signed up for this

            elif titles.CATALOG in text:
                message_text = 'لطفا دسته بندی را انتخاب کنید'
                category_titles = [category.title for category in categories]
                reply_markup = {
                            'keyboard': generate_keyboard(category_titles, True),
                            'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
                            'one_time_keyboard': False  # Optional: hide the keyboard after a button press
                        }
                self.telegram_service.send_message_with_keyboard(chat_id, message_text, reply_markup)

            elif titles.BACK in text:
                # If we are in category page we should show main menu
                reply_markup = {
                    'keyboard': generate_keyboard(),
                    'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
                    'one_time_keyboard': False  # Optional: hide the keyboard after a button press
                }
                self.telegram_service.send_message_with_keyboard(chat_id, 'لطفا گزینه موردنظر را انتخاب کنید', reply_markup)
                # If we are in

            elif text in [post.title for post in posts]:
                # Text matches a post title
                # Handle pages:
                # Get a list of all posts

                # compare text with posts titles
                post_titles = [post.title for post in posts]
                for post_title in post_titles:
                    if text == post_title:
                        # Get the post
                        post = Post.objects.get(title=post_title)
                        # determin if the post has image or video
                        file_type, _ = mimetypes.guess_type(post.media.name)

                        if post.media:
                            if file_type:
                                if file_type.startswith('image/'):
                                    # It's image
                                    self.telegram_service.send_photo_message(chat_id, post.media.name, post.content)
                                elif file_type.startswith('video/'):
                                    # It's video
                                    print("--------------------VIDEO--------------------")
                                    self.upload_video_to_telegram(chat_id, video_name=post.media.name, message=post.content, is_gift=False)
                                else:
                                    # It's invalid
                                    self.telegram_service.send_telegram_message(chat_id, post.content, False)
                        else:
                            self.telegram_service.send_telegram_message(chat_id, post.content, False)

            elif text in [category.title for category in categories]:
                category = Category.objects.get(title=text)
                self.telegram_service.send_product_choices(chat_id, category)
            else:
                reply_markup = {
                    'keyboard': generate_keyboard(),
                    'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
                    'one_time_keyboard': False  # Optional: hide the keyboard after a button press
                }
                self.telegram_service.send_message_with_keyboard(chat_id, 'گزینه وجود ندارد', reply_markup)


    def handle_callback_query(self, callback_query):
        chat_id = callback_query['from']['id']
        callback_data = callback_query.get('data')



        replies = []
        gifts = GiftItem.objects.all()
        for gift in gifts:
            replies.append(gift.title)

        product_replies = []
        products = Product.objects.all()
        for product in products:
            product_replies.append(product.title)

        if callback_data in replies:
            gift = GiftItem.objects.get(title=callback_data)
            if gift.gift_type == 'VI':
                self.telegram_service.send_telegram_message(chat_id, "در حال آپلود ویدئو...لطفا صبر کنید")
                self.upload_video_to_telegram(chat_id, video=gift)
            else:
                self.telegram_service.send_telegram_message(chat_id, "در حال آپلود فایل...لطفا صبر کنید")
                self.upload_pdf_to_telegram(chat_id, gift)
        elif callback_data in product_replies:
            product = Product.objects.get(title=callback_data)
            message = f'{product.title} \n\n {product.description}'
            if product.photo:
                self.telegram_service.send_photo_product(chat_id, product.photo, message, product.link_to_website, False)
            else:
                self.telegram_service.send_product(chat_id, message, product.link_to_website, False)




    def upload_video_to_telegram(self, chat_id, video=None, video_name='', message='', is_gift=True):
        url = f"https://api.telegram.org/bot{get_bot_token()}/sendVideo"
        video_path = ''  # Full path to the video file
        if video:
            # This is a gift item
            video_path = os.path.join(settings.MEDIA_ROOT, video.content.name)
        else:
            # This is a post item
            video_path = os.path.join(settings.MEDIA_ROOT, video_name)
        # self.send_chat_action(chat_id, 'upload_video')

        caption_text = f'{video.title}' if video else message

        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {
                'chat_id': chat_id,
                'caption': caption_text
            }
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                if is_gift:
                    self.telegram_service.send_telegram_message(chat_id, "هدیه با موفقیت ارسال شد", False)
                    current_user = Customer.objects.get(chat_id=chat_id)
                    current_user.has_recieved_gift = True
                    current_user.save()

                    video.download_count = video.download_count + 1
                    video.save()
            else:
                self.telegram_service.send_telegram_message(chat_id, "لطفا لحظاتی دیگر دوباره تلاش کنید", False)
            return response


    def upload_pdf_to_telegram(self, chat_id, pdf):
        url = f"https://api.telegram.org/bot{get_bot_token()}/sendDocument"
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf.content.name)  # Full path to the video file

        # self.send_chat_action(chat_id, 'upload_video')

        with open(pdf_path, 'rb') as pdf_file:
            files = {'document': pdf_file}
            data = {
                'chat_id': chat_id,
                'caption': f"{pdf.title} [PDF]"
            }
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                self.telegram_service.send_telegram_message(chat_id, "هدیه با موفقیت ارسال شد")
                current_user = Customer.objects.get(chat_id=chat_id)
                current_user.has_recieved_gift = True
                current_user.save()

                pdf.download_count = pdf.download_count + 1
                pdf.save()
            else:
                self.telegram_service.send_telegram_message(chat_id, "لطفا لحظاتی دیگر دوباره تلاش کنید")
            return response




@login_required
def user_list(request):
    user_list = Customer.objects.all()
    # Pagination with 12 people per page
    paginator = Paginator(user_list, 12)
    page_number = request.GET.get('page', 1)
    try:
        users = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        users = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        users = paginator.page(paginator.num_pages)
    context = {
        "users":users,
        "section":"people"
    }
    return render(request, 'bot/users/user_list.html', context)


@login_required
def post_list(request):
    post_list = Post.objects.all()
    # Pagination with 12 people per page
    paginator = Paginator(post_list, 12)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    media_path = os.path.join(settings.MEDIA_ROOT, '')
    context = {
        "posts":posts,
        "section":"posts",
        'media_path':media_path
    }

    return render(request, 'bot/posts/post_list.html', context)

@login_required
def post_add(request):
    telegram_service = TelegramService()
    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'صفحه با موفقیت اضافه شد')
            update_keyboard()
            return redirect('bot:posts')

    else:
        form = PostEditForm()

    context = {
        'form':form
    }

    return render(request, 'bot/posts/post_add.html', context)


@login_required
def post_delete(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        post.delete()
        return redirect('bot:posts')

@login_required
def post_edit(request, id):
    telegram_service = TelegramService()
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'صفحه با موفقیت بروزرسانی شد')
            update_keyboard()
            return redirect('bot:posts')

    else:
        form = PostEditForm(instance=post)

    context = {
        'post':post,
        'form':form
    }

    return render(request, 'bot/posts/post_edit.html', context)


@login_required
def broadcast(request):
    telegram_service = TelegramService()
    users = Customer.objects.all()
    number_of_users = Customer.objects.count()
    if request.method == 'POST':
        message = request.POST.get('w3review')
        reply_markup = {
            'keyboard': generate_keyboard(),
            'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
            'one_time_keyboard': False  # Optional: hide the keyboard after a button press
        }

        sent_messages = 0
        for user in users:
            try:
                telegram_service.send_message_with_keyboard(user.chat_id, message, reply_markup)
                sent_messages = sent_messages + 1
            except Exception as e:
                print("Error sending message for some users")

        messages.success(request, f'کل کاربران {number_of_users} تعداد پیام ارسالی: {sent_messages}')


    context = {
        'emojis':data.emojis
    }
    if Telebot.objects.exists():
        context['bot'] = 'True'

    return render(request, 'bot/broadcast.html', context)


def update_keyboard():
    users = Customer.objects.all()
    telegram_service = TelegramService()
    reply_markup = {
            'keyboard': generate_keyboard(),
            'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
            'one_time_keyboard': False  # Optional: hide the keyboard after a button press
        }
    message = ''
    for user in users:
        try:
            telegram_service.send_message_with_keyboard(user.chat_id, 'ربات بروزرسانی شد', reply_markup)
        except Exception as e:
            print("Error sending message for some users")



@login_required
def user_detail(request, id):
    telegram_service = TelegramService()
    user = Customer.objects.get(chat_id=id)
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if 'send_message' in request.POST:
            message = request.POST.get('w3review')
            try:
                reply_markup = {
                    'keyboard': generate_keyboard(),
                    'resize_keyboard': True,  # Optional: resize keyboard to fit the number of buttons
                    'one_time_keyboard': False  # Optional: hide the keyboard after a button press
                }
                telegram_service.send_message_with_keyboard(user.chat_id, message, reply_markup)
                messages.success(request, 'پیام شما با موفقیت ارسال شد')
            except Exception as e:
                messages.error(request, 'مشکلی پیش آمده، لطفا دوباره امحان کنید و یا با پشتیبانی تماس بگیرید')




    context = {
        'user':user,
        'emojis':data.emojis
    }

    if Telebot.objects.exists():
        context['bot'] = 'True'
    return render(request, 'bot/users/user_detail.html', context)



@login_required
def add_bot(request):
    if Telebot.objects.exists():
        return redirect('bot:edit_bot')

    if request.method == 'POST':
        form = RobotForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            bot_token = cd['token']
            url = settings.BASE_URL
            trim_url = url.split('//')[1]
            api_url = f'https://api.telegram.org/bot{bot_token}/setwebhook?url={trim_url}/bot/webhook/'
            print(api_url)
            res = requests.get(api_url)
            if res.status_code == 200:
                messages.success(request, 'ربات با موفقیت به سرور تلگرام متصل شد')
                return redirect('bot:edit_bot')
            else:
                messages.error(request, 'خطایی در هنگام اتصال به سرور تلگرام رخ داد، با دکمه بروزرسانی دوباره تلاش کنید')
                return redirect('bot:edit_bot')


    else:
        form = RobotForm()


    context = {
        'form':form,
        'emojis':data.emojis
    }

    return render(request, 'bot/add_bot.html', context)


@login_required
def edit_bot(request):
    bot = Telebot.objects.first()

    if request.method == 'POST':
        form = RobotForm(request.POST, request.FILES, instance=bot)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            bot_token = cd['token']
            url = settings.BASE_URL
            trim_url = url.split('//')[1]
            api_url = f'https://api.telegram.org/bot{bot_token}/setwebhook?url={trim_url}/bot/webhook/'
            print(api_url)
            res = requests.get(api_url)
            if res.status_code == 200:
                messages.success(request, 'ربات با موفقیت به سرور تلگرام متصل شد')
                return redirect('bot:edit_bot')
            else:
                messages.error(request, 'خطایی در هنگام اتصال به سرور تلگرام رخ داد، با دکمه بروزرسانی دوباره تلاش کنید')
                return redirect('bot:edit_bot')

    else:
        form = RobotForm(instance=bot)


    context = {
        'bot':bot,
        'form':form,
        'emojis':data.emojis
    }

    return render(request, 'bot/robot.html', context)
