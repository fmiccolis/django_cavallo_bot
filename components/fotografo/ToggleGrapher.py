from telegram import Update
from telegram.ext import CallbackQueryHandler, CallbackContext

from botLogger import logger as gra_logger
from components.fotografo.PhotographerUtil import update_and_show
from core.models import Photographer

extra = {'file_name': 'ToggleGrapher.py'}


def toggle_grapher_callback_handler(update: Update, context: CallbackContext):
    gra_logger.info(extra=extra, msg=f"Request toggle_grapher_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    photographer: Photographer = context.user_data['fotografo']
    photographer.status = not photographer.status
    photographer.save()
    message.delete()
    update_and_show(message, context, photographer, 'photographers', 'devs')


toggle_grapher_hand = CallbackQueryHandler(toggle_grapher_callback_handler, pattern='^(TOGGLE_PHOTOGRAPHER)$')
