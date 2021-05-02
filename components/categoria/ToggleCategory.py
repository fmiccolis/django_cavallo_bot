from telegram import Update
from telegram.ext import CallbackQueryHandler, CallbackContext

from botLogger import logger as cat_logger
from components.categoria.CategoryUtil import update_and_show
from core.models import Category

extra = {'file_name': 'ToggleCategory.py'}


def toggle_category_callback_handler(update: Update, context: CallbackContext):
    cat_logger.info(extra=extra, msg=f"Request toggle_category_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    try:
        categoria: Category = context.user_data['categoria']
        cat_logger.info(extra=extra, msg=f"{categoria}")
        categoria.status = not categoria.status
        categoria.save()
        message.delete()
        update_and_show(message, context, categoria, 'categories', 'devs')
    except Exception as E:
        cat_logger.error(extra=extra, msg=f"Request toggle_category_callback_handler. Error during toggling")
        cat_logger.error(extra=extra, msg=f"Errore {E}")


toggle_category_hand = CallbackQueryHandler(toggle_category_callback_handler, pattern='^(TOGGLE_CATEGORY)$')
