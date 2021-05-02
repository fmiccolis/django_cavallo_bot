import pickle

from django.core.files.base import ContentFile
from telegram import Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, Filters, \
    CallbackContext

from botConfig import cancel, CONV_TIMEOUT
from components.utilities import get_encodings_from_video
from botLogger import logger as tu_logger
from core.models import TelegramUser

NEWVIDEO = range(1)
extra = {'file_name': 'EditVideo.py'}


def edit_video_callback_handler(update: Update, context: CallbackContext):
    tu_logger.info(extra=extra, msg=f"Request edit_video_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    message.reply_text("Va bene, mandami un video come mostrato")
    message.reply_video(
        video=open('resources/gifs/face_id.gif', 'rb'),
        caption="Copia lo stesso movimento che vedi in questo video"
    )
    message.delete()
    return NEWVIDEO


def newvideo(update: Update, context: CallbackContext):
    tu_logger.info(extra=extra, msg=f"Request newvideo")
    message = update.message
    user_id = message.from_user.id
    tg_user: TelegramUser = TelegramUser.objects.get(pk=user_id)
    video_file = message.video.get_file()
    tg_user.url_video.save('video.mp4', ContentFile(video_file.download_as_bytearray()))

    message.reply_text(
        "Molto bene sto analizzando il video che mi hai inviato per processare e aggiornare i dati del tuo volto!"
    )

    all_face_encodings = get_encodings_from_video(tg_user.url_video.path)

    message.reply_text("Ho finito di analizzare!\nFra pochi istanti avrai i risultati.")

    if len(all_face_encodings) > 0:
        tu_logger.info(extra=extra, msg=f"Request newvideo. face founded: {len(all_face_encodings)}")
        try:
            tg_user.url_encodings.save('encodings.dat', ContentFile(pickle.dumps(all_face_encodings)))
            tg_user.save()

            message.reply_text('Perfetto ho salvato il tuo video!\nOra, cliccando su /invia, riceverai il tuo video.')
        except Exception as E:
            tu_logger.info(extra=extra, msg=f"Request newvideo. error while saving data {E}")
            message.reply_text('Non sono riuscito ad aggiornare il tuo video e i tuoi dati.\nRiprova più tardi')
    else:
        tu_logger.critical(extra=extra, msg=f"Request newvideo. no faces in video")
        message.reply_text("Per piacere inviami un video con un volto riconoscibile!")
        return edit_video_callback_handler(update, context)

    return ConversationHandler.END


edit_video_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_video_callback_handler, pattern='^(EDIT_VIDEO)$')],

    states={
        NEWVIDEO: [MessageHandler(Filters.video, newvideo)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
