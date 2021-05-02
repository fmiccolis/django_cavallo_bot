from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler,
                          CallbackContext)
from botConfig import EVENTS_PATH, delete_dir_and_content, cancel, CONV_TIMEOUT
import os
from botLogger import logger as gra_logger
from core.models import Photographer, Event

ARE_YOU_SURE = range(1)
extra = {'file_name': 'RemoveGrapher.py'}


def remove_grapher_callback_handler(update: Update, context: CallbackContext):
    gra_logger.info(extra=extra, msg=f"Request remove_grapher_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    fotografo: Photographer = context.user_data.get('fotografo', None)
    reply_keyboard = [
        ['Si, voglio essere rimosso'],
        ['No, voglio restare']
    ]
    message.reply_text("Sei sicuro di voler rimuovere il tuo account da fotografo?\n"
                       "(tutti gli eventi e le foto da te caricate verranno rimosse)",
                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=reply_keyboard,
                                                        one_time_keyboard=True))
    context.user_data['remove_grapher'] = fotografo
    return ARE_YOU_SURE


def remove_grapher(update: Update, context: CallbackContext):
    gra_logger.info(extra=extra, msg=f"Request remove_grapher")
    fotografo: Photographer = context.user_data['remove_grapher']
    try:
        events = Event.objects.filter(photographer=fotografo)
        events_path = [os.path.join(EVENTS_PATH, str(event.evento_id)) for event in events]
        fotografo.delete()
        msg = "Ok, sei stato rimosso dalla lista dei fotografi e come te anche tutti i tuoi eventi e le tue foto.\n" \
              "Ricordati che puoi sempre tornare creando una nuova /candidatura !!"
        delete_dir_and_content(events_path)
        gra_logger.info(extra=extra, msg=f"Request remove_grapher. deleted events")
    except Exception as E:
        gra_logger.error(extra=extra, msg=f"Request remove_grapher. events safe {E}")
        msg = "Non sono riuscito a eliminarti dalla lista dei fotografi " \
              "(i tuoi eventi e le tue foto sono ancora presenti nel mio database)"
    update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def dont_remove_grapher(update: Update, context: CallbackContext):
    gra_logger.info(extra=extra, msg=f"Request dont_remove_grapher")
    update.message.reply_text("Ok, non verrai rimosso!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


remove_grapher_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(remove_grapher_callback_handler, pattern='^(REMOVE_GRAPHER)$')],

    states={
        ARE_YOU_SURE: [
            MessageHandler(Filters.regex(r'Si'), remove_grapher),
            MessageHandler(Filters.regex(r'No'), dont_remove_grapher)
        ]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
