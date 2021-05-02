import re

from telegram import Update, ParseMode
from telegram.ext import MessageHandler, Filters, CallbackContext

from components.keyboards import keyboard_find_face
from botConfig import extract_event_info
from botLogger import logger as eve_logger
from core.models import Event

extra = {'file_name': 'GetSpecEvent.py'}


def single_event(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request single_event")
    try:
        isdev, code = update.message.text[8:].split('_')
        if isdev == 'd':
            context.user_data['is_dev_mode'] = True
    except ValueError as VE:
        code = update.message.text[8:]
    evento: Event = Event.objects.get(code=code)
    if evento:
        strbuilder = extract_event_info(evento, all_info=False)
        update.message.reply_text(
            strbuilder,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard_find_face
        )
        context.user_data['evento'] = evento
    else:
        eve_logger.critical(extra=extra, msg=f"Request single_event. no event with token {code}")
        update.message.reply_text(
            f"Non esiste nessun evento attivo associato con questo token:\n{code}\n\n"
            f"Il fotografo potrebbe averlo cambiato. Chiedi all\'organizzatore dell\'evento il nuovo token!"
        )


single_event_conv = MessageHandler(Filters.regex(re.compile(r'^/evento_')), single_event)
