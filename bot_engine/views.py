import json
from django.http import JsonResponse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import *
from selenium import webdriver
from datetime import datetime
from requests import post as send
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os.path
import inspect
import os

TELEGRAM_URL = 'https://api.telegram.org/bot'
BOT_TOKEN = os.environ.get('FOTO_BOT_TOKEN')


def screen_shot_maker (url):
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--disable-dev-shm-usage")
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)

    driver.get(url)
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.visibility_of_any_elements_located((By.XPATH, 'HTML')))
    way_to_images = os.path.join(os.path.join(os.path.dirname(os.path.abspath(filename)), 'static'), 'images')
    dt = str(datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f'))
    flnm = f'{url[:25]}_{dt}'.replace("/", "_").replace(".", "_")
    driver.save_screenshot(way_to_images+f'/{flnm}.png')
    driver.quit()

    return way_to_images+f'/{flnm}.png'


def validation_url(url):
    validate = URLValidator()
    try:
        validate(url)
        return True
    except ValidationError:
        return False


def send_message(chat_id, message, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": message,
        'reply_markup': keyboard,
    }
    send(f"{TELEGRAM_URL}{BOT_TOKEN}/sendMessage", data=data)
    JsonResponse({" ok ": " POST request processed"})


def send_image(chat_id, file, message):
    with open(file, "rb") as fl:
        dt = fl.read()

    data = {
        'chat_id': chat_id,
        'caption': message,
    }
    send(f"{TELEGRAM_URL}{BOT_TOKEN}/sendPhoto", files={'photo': dt},  data=data)
    return JsonResponse({" ok ": " POST request processed"})


def engine(request):
    data = json.loads(request.body)
    chat_id = data.get('message').get('chat').get('id')
    user_message = data.get('message').get('text')
    if validation_url(user_message):
        return send_image(chat_id=chat_id, file=screen_shot_maker(user_message), message=str(getattr
                         (Messages.objects.filter(using_place='text_with_screen_shot').first(), 'message')))
    elif user_message == '/start':
        send_message(chat_id=chat_id,
                     message=str(getattr(Messages.objects.filter(using_place='starting_message').first(),
                                         'message')))
    else:
        send_message(chat_id=chat_id, message=user_message + ' ' +
                    str(getattr(Messages.objects.filter(using_place='not_valid_url').first(), 'message')))

    return JsonResponse({" ok ": " POST request processed"})
