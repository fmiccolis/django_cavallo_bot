from typing import Union

from telegram import ParseMode, Message, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from components.keyboards import keyboard_navigation, keyboard_scan_edit
from botConfig import extract_event_info, generate_navigation_action
from core.models import Event


def update_and_show(
        message: Message,
        context: CallbackContext,
        evento: Union[Event, int],
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
            message.reply_text("Non ci sono più eventi", reply_markup=ReplyKeyboardRemove())
            return
        if current != 0:
            current -= 1
        else:
            current = 1
        info['total'] = total
        info['current'] = current
        context.user_data['evento'] = array[current]
        strbuilder = extract_event_info(array[current])
    else:
        array[current] = evento
        strbuilder = extract_event_info(evento)
    context.chat_data[in_action] = info
    keyboard = generate_navigation_action(keyboard_navigation, keyboard_scan_edit, current, total)
    if total == 1:
        keyboard = keyboard_scan_edit
    message.reply_text(strbuilder, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
