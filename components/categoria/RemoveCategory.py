from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from botLogger import logger as cat_logger
from botConfig import cancel, CONV_TIMEOUT
from core.models import Category

ARE_YOU_SURE = range(1)
extra = {'file_name': 'RemoveCategory.py'}


def remove_category_callback_handler(update: Update, context: CallbackContext):
    cat_logger.info(extra=extra, msg=f"Request remove_category_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    categoria: Category = context.user_data['categoria']
    if categoria:
        message.delete()
        reply_keyboard = [
            ['Si, voglio cancellare la categoria'],
            ['No, non cancellare la categoria']
        ]
        message.reply_text(f"Sei sicuro di voler rimuovere la categoria {categoria.name}?\n"
                           "(tutti gli eventi con questa categoria passeranno alla categoria di default)",
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=reply_keyboard,
                                                            one_time_keyboard=True))
    else:
        cat_logger.info(extra=extra, msg=f"Request remove_category_callback_handler. error during finding category")
    return ARE_YOU_SURE


def remove_category(update: Update, context: CallbackContext):
    cat_logger.info(extra=extra, msg=f"Request remove_category")
    categoria: Category = context.user_data['categoria']
    try:
        categoria.delete()
        msg = "Tutte gli eventi sono stati aggiornati e la categoria è stata rimossa"
        cat_logger.critical(extra=extra, msg=f"Request remove_category. edited events")
    except Exception as E:
        cat_logger.error(extra=extra, msg=f"Request remove_grapher. events safe {E}")
        msg = f"C\'è stato un errore durante l'aggiornamento degli eventi." \
              f"La categoria che volevi rimuovere è ancora presente"
    update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def dont_remove_category(update: Update, context: CallbackContext):
    cat_logger.info(extra=extra, msg=f"Request dont_remove_grapher")
    update.message.reply_text("Ok, la categoria non verrà rimossa!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


remove_category_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(remove_category_callback_handler, pattern='^(REMOVE_CATEGORY)$')],

    states={
        ARE_YOU_SURE: [
            MessageHandler(Filters.regex(r'Si'), remove_category),
            MessageHandler(Filters.regex(r'No'), dont_remove_category)
        ]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
