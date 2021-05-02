from telegram import Update, ParseMode, Message
from telegram.ext import CallbackQueryHandler, CallbackContext

from components.keyboards import keyboard_navigation, navigation
from botConfig import extraction_switcher, generate_navigation_action


def first_element_callback_hand(update: Update, context: CallbackContext):
    in_action = context.chat_data["in_action"]
    current = context.chat_data[in_action].get("current", None)
    return represent_data(update, context, current, 0, in_action)


def prev_element_callback_hand(update: Update, context: CallbackContext):
    in_action = context.chat_data["in_action"]
    current = context.chat_data[in_action].get("current", None)
    return represent_data(update, context, current, current-1, in_action)


def this_element_callback_hand(update: Update, context: CallbackContext):
    query = update.callback_query
    in_action = context.chat_data["in_action"]
    info = context.chat_data[in_action]
    total = info.get("total", None)
    current = info.get("current", None)
    query.answer(text=f"Elemento {current+1} su {total}")


def next_element_callback_hand(update: Update, context: CallbackContext):
    in_action = context.chat_data["in_action"]
    current = context.chat_data[in_action].get("current", None)
    return represent_data(update, context, current, current+1, in_action)


def last_element_callback_hand(update: Update, context: CallbackContext):
    in_action = context.chat_data["in_action"]
    from_pos = context.chat_data[in_action].get("current", None)
    to_pos = context.chat_data[in_action].get("total", None) - 1
    return represent_data(update, context, from_pos, to_pos, in_action)


def represent_data(update: Update, context: CallbackContext, from_pos: int, to_pos: int, in_action: str):
    query = update.callback_query
    query.answer()
    info = context.chat_data[in_action]
    total = info.get("total", None)
    array = info.get("array", None)
    if total != len(array):
        total = len(array)
    if from_pos == to_pos:
        return
    if to_pos < 0:
        return
    if to_pos > total-1:
        return
    message = update.effective_message
    level = context.chat_data['level']
    if array:
        strbuilder = extraction_switcher(array[to_pos], in_action)
        keyboard = generate_navigation_action(keyboard_navigation, navigation[in_action][level], to_pos, total)
        message.edit_text(
            strbuilder,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        info = {
            'array': array,
            'current': to_pos,
            'total': len(array)
        }
        context.chat_data[in_action] = info
        switcher = {
            'events': 'evento',
            'photographers': 'fotografo',
            'categories': 'categoria'
        }
        context.user_data[switcher[in_action]] = array[to_pos]
    else:
        message.reply_text("Errore durante il cambio!")


def init_navigation(message: Message, context: CallbackContext, array, choice: str, level: str):
    context.chat_data['in_action'] = choice
    context.chat_data['level'] = level
    info = {
        'array': array,
        'current': 0,
        'total': len(array)
    }
    context.chat_data[choice] = info
    strbuilder = extraction_switcher(array[0], choice)
    keyboard = generate_navigation_action(keyboard_navigation, navigation[choice][level], 0, len(array))
    if len(array) == 1:
        keyboard = navigation[choice][level]
    if strbuilder:
        message.reply_text(
            strbuilder,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN_V2
        )


first_element_hand = CallbackQueryHandler(first_element_callback_hand, pattern='^(FIRST_ELEMENT)$')
prev_element_hand = CallbackQueryHandler(prev_element_callback_hand, pattern='^(PREV_ELEMENT)$')
this_element_hand = CallbackQueryHandler(this_element_callback_hand, pattern='^(CURRENT_ELEMENT)$')
next_element_hand = CallbackQueryHandler(next_element_callback_hand, pattern='^(NEXT_ELEMENT)$')
last_element_hand = CallbackQueryHandler(last_element_callback_hand, pattern='^(LAST_ELEMENT)$')
