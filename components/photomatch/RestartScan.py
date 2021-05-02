from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, CommandHandler, \
    Filters

from botLogger import logger as pm_logger
from components import utilities
from botConfig import cancel, CONV_TIMEOUT
from core.models import PhotoMatch, Event

AREYOUSURE = range(1)
extra = {'file_name': 'RestartScan.py'}


def restart_scan(update: Update, context: CallbackContext):
    pm_logger.info(extra=extra, msg=f"Request restart_scan")
    query = update.callback_query
    query.answer()
    message = query.message
    evento: Event = context.user_data['evento']
    matches = PhotoMatch.objects.filter(photo__event=evento)
    if matches:
        keyboard_yes_no = [['Si'], ['No']]
        message.reply_text(
            "Degli utenti hanno già trovato i loro volti per questo evento!\n"
            "Ricominciando lo scanning del sito essi perderanno i salvataggi.\n\n"
            "Sei sicuro di voler continuare lo stesso?",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_yes_no, one_time_keyboard=True)
        )
        context.user_data["are_you_sure_evento"] = evento
        return AREYOUSURE
    context.user_data["evento"] = evento
    return utilities.start_scanning(update, context)


def yes_im_sure(update: Update, context: CallbackContext):
    pm_logger.info(extra=extra, msg=f"Request yes_im_sure")
    evento = context.user_data["are_you_sure_evento"]
    context.user_data["evento"] = evento
    update.message.reply_text("Ora ricomincerà la ricerca!", reply_markup=ReplyKeyboardRemove())
    return utilities.start_scanning(update, context)


def not_sure(update: Update, context: CallbackContext):
    pm_logger.info(extra=extra, msg=f"Request not_sure")
    update.message.reply_text("La nuova ricerca non partirà!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


restart_scan_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(restart_scan, pattern='^(RESTART_SCAN)$')],

    states={
        AREYOUSURE: [MessageHandler(Filters.regex('^(Si)$'), yes_im_sure),
                     MessageHandler(Filters.regex('^(No)$'), not_sure)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
