from hashlib import sha256

from telegram import Update, MessageEntity
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext)

from botLogger import logger as gra_logger
from botConfig import devs, cancel, CONV_TIMEOUT
from core.models import TelegramUser, Photographer

ADDNAME, ADDLINK, ADDIG = range(3)
extra = {'file_name': 'AddNewPhotographer.py'}


def candidatura(update: Update, context: CallbackContext):
    gra_logger.info(extra=extra, msg=f"Request candidatura")
    message = update.message
    user_id = message.from_user.id
    tg_user = TelegramUser.objects.get(pk=user_id)
    fotografo = Photographer.objects.filter(telegram_user=tg_user)
    if fotografo:
        message.reply_text(
            'Ciao, sei già registrato come fotografo!\n'
            'Per accedere all\'area a te dedicata usa il comando /gestione'
        )
        return ConversationHandler.END

    context.user_data['tg_user'] = tg_user
    message.reply_text('Ciao, allora vuoi essere inserito come fotografo per aggiungere i tuoi eventi? '
                       'Per prima cosa ho bisogno di sapere il tuo nome da fotografo!')
    return ADDNAME


def addname(update: Update, context: CallbackContext):
    message = update.message
    name = message.text
    gra_logger.info(extra=extra, msg=f"Request addname. name: {name}")
    context.user_data["nome_fotografo"] = name
    message.reply_text('Molto bene, adesso ho bisogno del link al tuo sito internet.\n\n'
                       'Se non hai un sito internet puoi saltare questa procedura usando il comando /salta')
    return ADDLINK


def addlink(update: Update, context: CallbackContext):
    message = update.message
    link = message.text
    context.user_data["url_sito"] = link
    if link == '/salta':
        context.user_data["url_sito"] = ""
    gra_logger.info(extra=extra, msg=f"Request addlink. link: {link}")
    message.reply_text(
        'Perfetto! Adesso inviami l\'username del tuo profilo instagram utilizzando il formato "@username"\n\n'
        'Se non hai un profilo instagram puoi saltare questa procedura usando il comando /salta'
    )
    return ADDIG


def addig(update: Update, context: CallbackContext):
    message = update.message
    insta = message.text
    if insta == '/salta':
        insta = ""
    else:
        insta = insta[1:]

    gra_logger.info(extra=extra, msg=f"Request addig. username: {insta}")
    tg_user: TelegramUser = context.user_data["tg_user"]
    url_sito = context.user_data["url_sito"]
    nome_fotografo = context.user_data["nome_fotografo"]
    try:
        fotografo = Photographer(
            telegram_user=tg_user,
            name=nome_fotografo,
            website=url_sito,
            instagram=insta
        )
        fotografo.save()
        message.reply_text('Ottimo! Ho salvato i tuoi dati, però ancora non puoi aggiungere i tuoi eventi. '
                           'Verrai contattato da uno degli amministratori che verificherà che tu non sia un '
                           'robot (come me)!\nSe l\'esito sarà positivo allora usando il comando /gestione '
                           'potrai accedere a tutte le funzionalità per aggiungere i tuoi fantastici eventi.')
    except Exception as E:
        gra_logger.error(extra=extra, msg=f"Errore {E}")

    for dev_id in devs:
        context.bot.send_message(dev_id, f"Ciao, l\'utente @{tg_user.username} ha richiesto "
                                         "di essere aggiunto come fotografo, contattalo e vedi che dice.")
    return ConversationHandler.END


create_new_photographer = ConversationHandler(
    entry_points=[CommandHandler("candidatura", candidatura)],

    states={
        ADDNAME: [MessageHandler(Filters.text & (~Filters.command), addname)],

        ADDLINK: [MessageHandler(Filters.entity("url"), addlink), CommandHandler("salta", addlink)],

        ADDIG: [MessageHandler(Filters.entity(MessageEntity.MENTION), addig), CommandHandler("salta", addig)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
