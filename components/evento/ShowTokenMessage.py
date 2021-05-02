from telegram import Update, ReplyKeyboardRemove, ParseMode
from telegram.ext import CallbackQueryHandler, CallbackContext

from botConfig import template_token_msg
from core.models import Event
from botLogger import logger as eve_logger

extra = {'file_name': 'ShowTokenMessage.py'}


def token_message(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request token_message")
    query = update.callback_query
    query.answer()
    message = query.message
    evento: Event = context.user_data.get('evento', False)
    if evento:
        message.reply_text(
            template_token_msg.format(nome_comando=evento.name, token=evento.code, context=context),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.HTML
        )


token_message_conv = CallbackQueryHandler(token_message, pattern='^(TOKEN_MESSAGE)$')
