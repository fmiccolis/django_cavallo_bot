from typing import Union

from telegram import ParseMode, Message, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from components.keyboards import keyboard_navigation, navigation
from botConfig import generate_navigation_action, extract_photographer_info
from core.models import Photographer


def update_and_show(
        message: Message,
        context: CallbackContext,
        fotografo: Union[Photographer, int],
        choice: str,
        level: str,
        is_remove: bool = False
):
    in_action = context.chat_data['in_action']
    info = context.chat_data[in_action]
    current = info.get("current", None)
    total = info.get("total", None)
    array = info.get("array", None)
    if is_remove:
        array.pop(current)
        total -= 1
        if total == 0:
            message.reply_text("Non ci sono più fotografi", reply_markup=ReplyKeyboardRemove())
            return
        if current != 0:
            current -= 1
        else:
            current = 1
        info['total'] = total
        info['current'] = current
        context.user_data['fotografo'] = array[current]
        strbuilder = extract_photographer_info(array[current])
    else:
        array[current] = fotografo
        strbuilder = extract_photographer_info(fotografo)
    context.chat_data[in_action] = info
    keyboard = generate_navigation_action(keyboard_navigation, navigation[choice][level], current, total)
    if total == 1:
        keyboard = navigation[choice][level]
    message.reply_text(strbuilder, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
