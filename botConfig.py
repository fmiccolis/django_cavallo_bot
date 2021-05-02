import calendar
import locale
import math
import os
import shutil
import sys
import traceback
from datetime import datetime
from functools import wraps

import emoji
import validators
from telegram import (ReplyKeyboardRemove, ParseMode, Update, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import ConversationHandler, CallbackContext
from telegram.utils.helpers import mention_html
import django

from botLogger import logger as conf_logger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cavallo_bot.settings')
django.setup()

from core.models import Event, Photo, Photographer, Category

TOKEN = "1190304453:AAF4OOJ3xRe-EUkmyCaWikpJSqdLPSXkF9M"

EVENTS_PATH = 'resources/eventi'
EVENT_ZIP_PATH = 'resources/eventi/{0}/zipped'
EVENT_PHOTOS_PATH = 'resources/eventi/{0}/photos'
EVENT_ENCODINGS_PATH = 'resources/eventi/{0}/encodings'

CONV_TIMEOUT = 300
EARTH_RADIUS: int = 6371
INSTAGRAM_BASE_URL = 'https://www.instagram.com/{0}'

devs = [337315288]
all_emojis = emoji.UNICODE_EMOJI['it']
locale.setlocale(0, "it")
months = [calendar.month_name[month + 1] for month in range(12)]


template_token_msg = "Ciao! ecco il token da utilizzare per trovare l\'evento \'{nome_comando}\'\n\n" \
                     "<pre>/evento_{token}</pre>\n\n" \
                     "Usa il comando /evento_<i>token</i> sul bot telegram:\n " \
                     "https://t.me/{context.bot.username}"

extra = {'file_name': 'config.py'}


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Ciao! Spero di poter parlare ancora con te un giorno.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def create_dir(new_dirs):
    created_dirs = list()
    for new_dir in new_dirs:
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        created_dirs.append(new_dir)
    return created_dirs


def delete_dir_and_content(old_dir_list):
    for dirtoremove in old_dir_list:
        if os.path.isdir(dirtoremove):
            for encodings in os.listdir(dirtoremove):
                path_encodings = os.path.join(dirtoremove, encodings)
                try:
                    if os.path.isfile(path_encodings) or os.path.islink(path_encodings):
                        os.unlink(path_encodings)
                    elif os.path.isdir(path_encodings):
                        shutil.rmtree(path_encodings)
                except Exception as e:
                    print('Impossibile cancellare {0}. Motivo {1}'.format(path_encodings, e))
            os.rmdir(dirtoremove)


def get_year_keyboard():
    keyboard_years = list()
    this_line = list()
    current_year = datetime.now().year
    for idx in range(20):
        if len(this_line) >= 4:
            keyboard_years.append(this_line.copy())
            this_line.clear()
        this_line.append(current_year - idx)
    keyboard_years.append(this_line.copy())
    return keyboard_years


def get_month_keyboard(year):
    now = datetime.now()
    current_year = now.year
    last_month = 12
    if year == current_year:
        last_month = now.month
    return iterate_month(last_month)


def iterate_month(last_month):
    month_keyboard = list()
    this_line = list()
    for month in range(last_month):
        if len(this_line) >= 3:
            month_keyboard.append(this_line.copy())
            this_line.clear()
        this_line.append(calendar.month_name[month + 1])
    month_keyboard.append(this_line)
    return month_keyboard


def get_days_by_month_and_year(month, year):
    now = datetime.now()
    starts_with, day_in_month = calendar.monthrange(year, month)
    if now.year == year:
        if now.month == month:
            day_in_month = now.day

    return iterate_day(day_in_month)


def iterate_day(days):
    day_keyboard = list()
    this_line = list()
    for day in range(days):
        if len(this_line) >= 5:
            day_keyboard.append(this_line.copy())
            this_line.clear()
        this_line.append((day + 1))
    day_keyboard.append(this_line)
    return day_keyboard


def dev_restricted(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        message = update.effective_message
        if user_id not in devs:
            conf_logger.info(extra=extra, msg=f"Unauthorized access denied for {user_id}")
            message.reply_text("Attenzione, questa è una zona riservata!\nNon puoi accedere a quest\'area!")
            return ConversationHandler.END
        return func(update, context, *args, *kwargs)

    return wrapped


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update: Update, context: CallbackContext, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


def distance_location_km(lat1: float, lon1: float, lat2: float, lon2: float):
    d_lat = deg2rad(lat2-lat1)
    d_lon = deg2rad(lon2-lon1)
    a = math.sin(d_lat/2) * math.sin(d_lat/2) + \
        math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * \
        math.sin(d_lon/2) * math.sin(d_lon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return EARTH_RADIUS * c


def deg2rad(deg) -> float:
    return deg * (math.pi/180)


def generate_navigation_action(
        keyboard_navigation: list,
        keyboard_action: InlineKeyboardMarkup,
        current: int,
        total: int
) -> InlineKeyboardMarkup:
    prev_hand = keyboard_action.inline_keyboard
    runtime_navigation = keyboard_navigation.copy()
    runtime_navigation.insert(2, InlineKeyboardButton(text=f"{current+1}/{total}", callback_data="CURRENT_ELEMENT"))
    enclosed = [runtime_navigation]
    for row in prev_hand:
        enclosed.append(row)
    return InlineKeyboardMarkup(enclosed)


def extraction_switcher(element, choiche, all_info: bool = True):
    switcher = {
        'events': extract_event_info,
        'photographers': extract_photographer_info,
        'categories': extract_category_info
    }
    return switcher[choiche](element, all_info)


def extract_photographer_info(fotografo: Photographer, all_info=True):
    status = 'attivo :white_check_mark:' if fotografo.status else 'disattivo :cross_mark:'
    eventi = Event.objects.filter(photographer=fotografo)
    active_events = len([evento for evento in eventi if evento.status == 1])
    strbuilder = f'*nome*: {fotografo.name}\n'
    if fotografo.website:
        strbuilder += f'*sito web*: [vai al sito]({fotografo.website})\n'
    if fotografo.instagram:
        strbuilder += f'*instagram*: [{fotografo.instagram}]({INSTAGRAM_BASE_URL.format(fotografo.instagram)})\n'
    strbuilder += f'*eventi caricati*: {active_events}\n'
    if all_info:
        strbuilder += f'*stato*: {emoji.emojize(status, use_aliases=True)}'
    return strbuilder


def extract_event_info(evento: Event, all_info=True):
    category = evento.category
    fotografo = evento.photographer
    real_date = evento.date.strftime("%d %B %Y")
    photos = Photo.objects.filter(event=evento)
    no_faces_photos = [photo for photo in photos if photo.faces is None]
    status = 'attivo :white_check_mark:' if evento.status else 'disattivo :cross_mark:'
    visibility = "Pubblico :busts_in_silhouette:" if evento.is_public else "Privato :lock:"
    master_url = fotografo.website
    if not master_url:
        master_url = INSTAGRAM_BASE_URL.format(fotografo.instagram)
    if validators.url(evento.url):
        url = evento.url
    else:
        drive, path_and_file = os.path.splitdrive(evento.url)
        path, file = os.path.split(path_and_file)
        url = file.replace('.', '\.').replace('_', '\_').replace('-', '\-')
    strbuilder = None
    if category is not None:
        category_name = category.name
        strbuilder = f'{emoji.emojize(":camera_with_flash:", use_aliases=True)}\t[{fotografo.name}]({master_url})\n' \
                     f'{emoji.emojize(":bust_in_silhouette:", use_aliases=True)}\t{evento.name}\n'
        if evento.description != "":
            strbuilder += f'{emoji.emojize(":memo:", use_aliases=True)}\t{evento.description}\n'
        strbuilder += f'{emoji.emojize(":globe_with_meridians:", use_aliases=True)}\t[vai al sito]({url})\n' \
                      f'{emoji.emojize(":symbols:", use_aliases=True)}\t{category_name} {emoji.emojize(category.emoji, use_aliases=True)}\n' \
                      f'{emoji.emojize(":date:", use_aliases=True)}\t{real_date}\n'
        if all_info:
            strbuilder += f'{emoji.emojize(":eye:", use_aliases=True)}\t{emoji.emojize(visibility, use_aliases=True)}\n'
        strbuilder += f'{emoji.emojize(":framed_picture:", use_aliases=True)}\t{len(photos)} \({len(photos) - len(no_faces_photos)} con volti\)\n'
        if all_info:
            strbuilder += f'{emoji.emojize(":vertical_traffic_light:", use_aliases=True)}\t{emoji.emojize(status, use_aliases=True)}'
    return strbuilder


def extract_category_info(categoria: Category, all_info=True):
    status = 'attivo :white_check_mark:' if categoria.status else 'disattivo :cross_mark:'
    strbuilder = f'*nome*: {categoria.name} {emoji.emojize(categoria.emoji)}\n' \
                 f'*descrizione*: {categoria.description}\n'
    if all_info:
        strbuilder += f'*stato*: {emoji.emojize(status, use_aliases=True)}'
    return strbuilder


def get_time_left(start_time: datetime, idx: int, total: int) -> str:
    current_time = datetime.now()
    elapsed_time = current_time - start_time
    time_left = total * elapsed_time / (idx + 1) - elapsed_time
    decimal, tot_sec = math.modf(time_left.total_seconds())
    m, s = divmod(int(tot_sec), 60)
    if s == 0 and m == 0:
        return 'fine'
    if m == 0:
        return f'{s} second{"o" if s == 1 else "i"}'
    if s == 0:
        return f'{m} minut{"o" if m == 1 else "i"}'
    return f'{m} minut{"o" if m == 1 else "i"} e {s} second{"o" if s == 1 else "i"}'


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + "'" + str(key) + "':", end='')
        tipo = str(type(value))
        if "User" in tipo:
            value = vars(value)
        elif "Message" in tipo:
            value = vars(value)
        elif "Chat" in tipo:
            value = vars(value)
        elif "CallbackQuery" in tipo:
            value = vars(value)

        if isinstance(value, dict):
            print(('\t' * (indent + 1)) + "{")
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


def horserace(percent):
    percent_min = round(percent / 10)
    horsemoji = ":horse:"
    pista = horsemoji * percent_min + str(percent) + "%\n"
    return emoji.emojize(string=pista, use_aliases=True)


# this is a general error handler function. If you need more information about specific type of update, add it to the
# payload in the respective if clause
def boterror(update, context: CallbackContext) -> None:
    # we want to notify the user of this problem. This will always work, but not notify encodings if the update is an
    # callback or inline query, or a poll update. In case you want this, keep in mind that sending the message
    # could fail
    if update.effective_message:
        text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. " \
               "My developer(s) will be notified."
        update.effective_message.reply_text(text)
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""
    # normally, we always have an user. If not, its either a channel or a poll update.
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
           f"</code>\n\nCheckout the <a href='https://python-telegram-bot.readthedocs.io/en/stable/'>telegram " \
           f"framework documentation</a> if there are some problems."
    # and send it to the dev(s)
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise
