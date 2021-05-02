from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Filters, CallbackQueryHandler, \
    CallbackContext
from botConfig import delete_dir_and_content, cancel, CONV_TIMEOUT
from botLogger import logger as tu_logger
from core.models import TelegramUser

ARE_YOU_SURE = range(1)
extra = {'file_name': 'RemoveVideo.py'}


def remove_video_callback_handler(update: Update, context: CallbackContext):
    tu_logger.info(extra=extra, msg=f"Request remove_video_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    reply_keyboard = [
        ['Si, voglio rimuovere il mio video'],
        ['No, voglio che il mio video resti']
    ]
    message.reply_text(
        "Sei sicuro di voler rimuovere il tuo video?\n"
        "La codifica del tuo volto verrà anch\'essa cancellata",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=reply_keyboard, one_time_keyboard=True)
    )
    return ARE_YOU_SURE


def remove_video_data(update: Update, context: CallbackContext):
    tu_logger.info(extra=extra, msg=f"Request remove_video_data")
    message = update.message
    user_id = message.from_user.id
    try:
        tg_user: TelegramUser = TelegramUser.objects.get(pk=user_id)
        events_path = [tg_user.url_encodings.path, tg_user.url_video.path]
        tg_user.url_video = None
        tg_user.url_encodings = None
        msg = "Ok, ho rimosso il video e i dati del tuo volto.\n" \
              "Ricordati che puoi sempre ricaricarli usando il comando /invia !!"
        delete_dir_and_content(events_path)
    except Exception as E:
        tu_logger.info(extra=extra, msg=f"Request remove_video_data. video not removed {E}")
        msg = "Non sono riuscito a eliminare il video e i dati del tuo volto"
    message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def dont_remove_video_data(update: Update, context: CallbackContext):
    tu_logger.info(extra=extra, msg=f"Request dont_remove_video_data")
    update.message.reply_text("Ok, non rimuoverò il video e i dati del tuo volto", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


remove_video_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(remove_video_callback_handler, pattern='^(REMOVE_VIDEO)$')],

    states={
        ARE_YOU_SURE: [
            MessageHandler(Filters.regex(r'Si'), remove_video_data),
            MessageHandler(Filters.regex(r'No'), dont_remove_video_data)
        ]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
