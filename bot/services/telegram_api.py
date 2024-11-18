import os
import json
from django.core.files.base import ContentFile
from bot.models import Telebot, Post
import requests
import logging
from django.core.exceptions import ObjectDoesNotExist
from gift.models import GiftItem
from django.conf import settings
from catalog.models import Product
from bot import titles

# Configure logging
# logger = logging.getLogger('core')

class TelegramService:
    def __init__(self):
        self.api_url = f'https://api.telegram.org/bot{self.get_bot_token()}/'

    @property
    def token(self):
        return self.get_bot_token()

    def get_bot_token(self):
        try:
            bot = Telebot.objects.first()
            return bot.token if bot else None
        except Exception as e:
            # Handle the exception (e.g., log it)
            return None

    def send_request(self, method, payload):
        try:
            url = f"{self.api_url}{method}"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raises an error for 4xx/5xx responses
            return response.json()
        except requests.exceptions.RequestException as e:
            # logger.error(f"Failed to call Telegram API: {e}")
            raise Exception(f"Error calling Telegram API: ==> {e.response}")

    def send_message_with_keyboard(self, chat_id, message, keyboard=None):
        payload = {
            'chat_id': chat_id,
            'text': message,
            'reply_markup': keyboard or {}
        }
        return self.send_request("sendMessage", payload)

    def send_gift_choices(self, chat_id):
        gifts = GiftItem.objects.all()
        keyboard = {'inline_keyboard': [], 'remove_keyboard': False}

        for i in range(0, len(gifts), 2):
            row = []
            for gift in gifts[i:i + 2]:
                button = {'text': gift.title, 'callback_data': gift.title}
                row.append(button)
            keyboard['inline_keyboard'].append(row)

        return self.send_message_with_keyboard(chat_id, 'هدیه خود را انتخاب کنید', keyboard)

    def send_product_choices(self, chat_id, category):
        products = Product.objects.filter(category=category)
        keyboard = {'inline_keyboard': [], 'remove_keyboard': False}

        for i in range(0, len(products), 2):
            row = []
            for product in products[i:i + 2]:
                button = {'text': product.title, 'callback_data': product.title}
                row.append(button)
            keyboard['inline_keyboard'].append(row)

        return self.send_message_with_keyboard(chat_id, 'محصول را انتخاب کنید', keyboard)

    def send_telegram_message(self, chat_id, message, remove_keyboard=False):
        keyboard = {'remove_keyboard': remove_keyboard}
        return self.send_message_with_keyboard(chat_id, message, keyboard)

    def send_reply_message(self, chat_id, message):
        keyboard = {'force_reply': True}
        return self.send_message_with_keyboard(chat_id, message, keyboard)

    def send_welcome_message(self, chat_id):
        try:
            bot = Telebot.objects.first()
            message = bot.welcome_message if bot else "Welcome!"
            picture = bot.welcome_picture.name
            picture_path = f'{settings.BASE_URL}{settings.MEDIA_URL}{picture}'
            posts = Post.objects.all()
            post_title = [post.title for post in posts]  # Extract the titles from the Post objects
            new_keyboard = self.generate_item_list(post_title, titles.GET_PERSONAL_ASSISTANCE, titles.RECIEVE_GIFT, titles.CATALOG)
            reply_markup = {
                'keyboard': new_keyboard,
                'resize_keyboard': True,
                'one_time_keyboard': False
            }

            payload = {
                'chat_id': chat_id,
                'photo':picture_path,
                'caption': message,
                'reply_markup':reply_markup
            }

            return self.send_request("sendPhoto", payload)
        except ObjectDoesNotExist:
            return self.send_telegram_message(chat_id, "خوش آمدید")


    def generate_item_list(self, items, fixed_item1, fixed_item2, fixed_item3, chunk_size=2):
        # Initialize the result list with the two distinct fixed items
        result = [[fixed_item1, fixed_item2], [fixed_item3]]

        # Loop through the items and group them in chunks of 'chunk_size'
        for i in range(0, len(items), chunk_size):
            result.append(items[i:i + chunk_size])

        return result


    def send_photo_message(self, chat_id, picture_name, message, remove_keyboard=False):
        picture_path = f'{settings.BASE_URL}{settings.MEDIA_URL}{picture_name}'
        payload = {
            'chat_id': chat_id,
            'photo':picture_path,
            'caption': message,
            'reply_markup': {'remove_keyboard': remove_keyboard}
        }
        # Ideally, you should send the photo using the sendPhoto method
        return self.send_request("sendPhoto", payload)


    def send_video_post(self, chat_id, video_name, message):
        video_path = os.path.join(settings.MEDIA_ROOT, video_name)  # Full path to the video file
        method = "sendVideo"
        # self.send_chat_action(chat_id, 'upload_video')

        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {
                'chat_id': chat_id,
                'caption': message
            }
            url = f"{self.api_url}{method}"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, files=files)
            if response.status_code == 200:
                print("DONE")



    def send_photo_product(self, chat_id, picture_name, message, url_to_website, remove_keyboard=False):
        picture_path = f'{settings.BASE_URL}{settings.MEDIA_URL}{picture_name}'

        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "مشاهده محصول",
                        "url": url_to_website
                    }
                ]
            ],
            'remove_keyboard': remove_keyboard
        }

        payload = {
            'chat_id': chat_id,
            'photo':picture_path,
            'caption': message,
            'reply_markup': keyboard
        }
        # Ideally, you should send the photo using the sendPhoto method
        return self.send_request("sendPhoto", payload)

    def send_product(self, chat_id, message, url_to_website, remove_keyboard=False):
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "مشاهده محصول",
                        "url": url_to_website
                    }
                ]
            ],
            'remove_keyboard': remove_keyboard
        }
        return self.send_message_with_keyboard(chat_id, message, keyboard)

