from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from components.evento.EventUtil import update_and_show
from botConfig import EVENTS_PATH, delete_dir_and_content, cancel, CONV_TIMEOUT
import os
from core.models import Event
from botLogger import logger as eve_logger

ARE_YOU_SURE = range(1)

extra = {'file_name': 'RemoveEvent.py'}


def remove_event_callback_handler(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request remove_event_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    evento: Event = context.user_data['evento']
    reply_keyboard = [
        ['Si, voglio rimuovere l\'evento'],
        ['No, non voglio rimuovere l\'evento']
    ]
    message.reply_text(f"Sei sicuro di voler rimuovere l\'evento {evento.name}?",
                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=reply_keyboard, one_time_keyboard=True))
    return ARE_YOU_SURE


def remove_event(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request remove_event")
    message = update.message
    try:
        evento: Event = context.user_data['evento']
        evento.delete()
        message.reply_text("Ok l\'evento è stato rimosso", reply_markup=ReplyKeyboardRemove())
        update_and_show(message, context, evento, True)
        delete_dir_and_content([os.path.join(EVENTS_PATH, str(evento.id))])
    except Exception as E:
        message.reply_text("Mi dispiace non sono riuscito a rimuovere l\'evento, riprova",
                           reply_markup=ReplyKeyboardRemove())
        eve_logger.error(extra=extra, msg=f"Errore {E}")
    return ConversationHandler.END


def dont_remove_event(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request dont_remove_event")
    update.message.reply_text("Ok, non rimuoverò l\'evento", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


remove_event_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(remove_event_callback_handler, pattern='^(REMOVE_EVENT)$')],

    states={
        ARE_YOU_SURE: [
            MessageHandler(Filters.regex(r'Si'), remove_event),
            MessageHandler(Filters.regex(r'No'), dont_remove_event)
        ]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
