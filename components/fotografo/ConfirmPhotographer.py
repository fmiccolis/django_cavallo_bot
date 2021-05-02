from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from botLogger import logger as gra_logger
from components.navigation import init_navigation
from botConfig import dev_restricted
from core.models import Photographer

extra = {'file_name': 'ConfirmPhotographer.py'}


@dev_restricted
def fotografi(update: Update, context: CallbackContext):
    gra_logger.info(extra=extra, msg=f"Request fotografi")
    message = update.message
    photographers = Photographer.objects.all()
    if not photographers:
        gra_logger.critical(extra=extra, msg=f"Request fotografi. there are no photographers")
        message.reply_text("Non ci sono fotografi!")
        return
    gra_logger.info(extra=extra, msg=f"Request fotografi. total photographers: {len(photographers)}")
    message.reply_text(f'Ciao, ci sono {len(photographers)} fotografi.\n\nEcco qui le loro informazioni:')
    init_navigation(message, context, list(photographers), 'photographers', 'devs')
    context.user_data['fotografo'] = photographers[0]


confirm_photographer = CommandHandler("fotografi", fotografi)
