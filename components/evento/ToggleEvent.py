from telegram import Update
from telegram.ext import CallbackQueryHandler, CallbackContext

from components.evento.EventUtil import update_and_show
from botLogger import logger as eve_logger
from core.models import Event

extra = {'file_name': 'ToggleEvent.py'}


def toggle_event_callback_handler(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request toggle_event_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    evento: Event = context.user_data['evento']
    evento.status = not evento.status
    evento.save()
    if evento:
        message.delete()
        update_and_show(message, context, evento)
    else:
        eve_logger.error(extra=extra, msg=f"Request toggle_event_callback_handler. error during toggling")
        query.message.reply_text("Errore durante l\'operazione")


toggle_event_hand = CallbackQueryHandler(toggle_event_callback_handler, pattern='^(TOGGLE_EVENT)$')
