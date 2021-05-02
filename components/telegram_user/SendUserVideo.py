import pickle

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ChatAction
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext

from botConfig import cancel, CONV_TIMEOUT, send_action
from botLogger import logger as tu_logger
from components.keyboards import keyboard_toggle_edit_video_data
from components.utilities import get_encodings_from_video
from core.models import TelegramUser
from django.core.files.base import ContentFile

PREPARATION, VIDEO = range(2)

extra = {'file_name': 'SendUserVideo.py'}


@send_action(ChatAction.RECORD_VIDEO_NOTE)
def invia(update: Update, context: CallbackContext):
    message = update.message
    user_id = message.from_user.id
    # store the video from the user
    reply_keyboard = [['Si', 'No']]
    tg_user: TelegramUser = TelegramUser.objects.get(pk=user_id)

    if bool(tg_user.url_encodings) and bool(tg_user.url_video):
        tu_logger.info(extra=extra, msg=f"{tg_user.url_video} exist")
        message.reply_text("Hai già salvato il tuo video, ora te lo mando...")
        context.bot.send_video(
            chat_id=user_id,
            video=open(tg_user.url_video.path, 'rb'),
            caption="Ecco il video che mi hai inviato",
            reply_markup=keyboard_toggle_edit_video_data
        )
        return ConversationHandler.END
    else:
        if tg_user.url_encodings.name is None:
            tu_logger.critical(extra=extra, msg="encodings not exist")
        else:
            tu_logger.critical(extra=extra, msg="video not exist")
        message.reply_text("Non ho trovato il tuo video nel mio database. Vuoi salvare il video?",
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=reply_keyboard, one_time_keyboard=True))
        context.user_data['tg_user'] = tg_user
        return PREPARATION


@send_action(ChatAction.RECORD_VIDEO_NOTE)
def saidyes(update: Update, context: CallbackContext):
    """The user want to store his photo in the bot"""
    message = update.message
    user = message.from_user
    tu_logger.info(extra=extra, msg=f"L\'utente {user.first_name} {user.last_name}: vuole salvare il suo video")
    message.reply_text('Molto bene! Per piacere, inviami un video come mostrato', reply_markup=ReplyKeyboardRemove())
    message.reply_video_note(
        video_note=open('static/gifs/face_id.gif', 'rb')
    )
    return VIDEO


def saidno(update: Update, context: CallbackContext):
    """The user want to store his photo in the bot"""
    message = update.message
    user = message.from_user
    tu_logger.info(extra=extra, msg=f"L\'utente {user.first_name} {user.last_name}: non vuole salvare il suo video")
    message.reply_text('Ok, non c\'è problema. Torna quando vuoi, Ciaoo!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def video(update: Update, context: CallbackContext):
    message = update.message
    user_id = message.from_user.id
    video_file = message.video.get_file()
    tg_user: TelegramUser = context.user_data['tg_user']
    tg_user.url_video.save('video.mp4', ContentFile(video_file.download_as_bytearray()))

    tu_logger.info(extra=extra, msg="beginning of the video analysis")
    message.reply_text(
        "Molto bene sto analizzando il video che mi hai inviato per processare e salvare i dati del tuo volto!"
    )
    all_face_encodings = get_encodings_from_video(tg_user.url_video.path)

    tu_logger.info(extra=extra, msg="End of the video analysis")
    message.reply_text("Ho finito di analizzare!\nFra pochi istanti avrai i risultati.")

    if len(all_face_encodings) > 0:
        try:
            tg_user.url_encodings.save('encodings.dat', ContentFile(pickle.dumps(all_face_encodings)))
            tg_user.save()
            tu_logger.info(extra=extra, msg=f"{user_id} encodings saved in {tg_user.url_encodings.path}")
            tu_logger.info(extra=extra, msg=f"Video of {user_id}: {tg_user.url_video.path}")
            message.reply_text('Perfetto ho salvato il tuo video!\nOra, cliccando su /invia, riceverai il tuo video.')
        except Exception as E:
            tu_logger.error(extra=extra, msg=f"Error while saving video data {E}")
            message.reply_text(
                "Ci scusiamo per l'inconveniente, non siamo riusciti a salvare i dati del tuo volto.\n"
                "Ti invitiamo a riprovare!"
            )
    else:
        tu_logger.critical(extra=extra, msg="video without faces")
        message.reply_text("Per piacere inviami un video con un volto riconoscibile!")
        return invia(update, context)

    return ConversationHandler.END


send_user_video = ConversationHandler(
    entry_points=[CommandHandler("invia", invia)],

    states={
        PREPARATION: [MessageHandler(Filters.regex('^(Si)$'), saidyes),
                      MessageHandler(Filters.regex('^(No)$'), saidno)],

        VIDEO: [MessageHandler(Filters.video, video)],
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
