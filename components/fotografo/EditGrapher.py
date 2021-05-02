from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, MessageEntity)
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from botLogger import logger as gra_logger
from components.fotografo.PhotographerUtil import update_and_show
from components.utilities import validate_ig_username
from botConfig import cancel, CONV_TIMEOUT
from core.models import Photographer

WHATTOEDIT, EDITNAME, EDITURL, EDITIG = range(4)
editable = ['nome', 'url', 'instagram']
extra = {'file_name': 'EditGrapher.py'}


def edit_grapher_callback_handler(update: Update, context: CallbackContext):
    gra_logger.info(extra=extra, msg=f"Request edit_grapher_callback_handler")
    query = update.callback_query
    query.answer()
    message = query.message
    msgid = message.message_id
    photographer: Photographer = context.user_data['fotografo']
    editable_keyboard = [[column] for column in editable]
    message.reply_text(
        "Ok scegli quale informazione modificare per il account da fotografo",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=editable_keyboard, one_time_keyboard=True)
    )
    context.user_data['edit_grapher'] = photographer
    context.user_data['msg_to_delete'] = msgid
    return WHATTOEDIT


def what_to_edit(update: Update, context: CallbackContext):
    swithcer = {
        'nome': edit_name_switch,
        'url': edit_url_switch,
        'instagram': edit_ig_switch
    }
    gra_logger.info(extra=extra, msg=f"Request what_to_edit. edit: {update.message.text}")
    return swithcer[update.message.text](update, context)


def edit_name_switch(update: Update, context: CallbackContext):
    update.message.reply_text("Ok scegli il tuo nuovo nome da fotografo", reply_markup=ReplyKeyboardRemove())
    return EDITNAME


def edit_name(update: Update, context: CallbackContext):
    photographer: Photographer = context.user_data['edit_grapher']
    return param_switcher(update, context, photographer, 'nome', update.message.text, 'il nome')


def edit_url_switch(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Ok scegli il nuovo url per il tuo sito.\nTi ricordo di sfruttare la funzione "
        "copia e incolla del tuo smartphone o pc per essere sicuro di inserire un link valido.\n"
        "Se non hai un sito web oppure non vuoi inserirlo usa il comando /salta",
        reply_markup=ReplyKeyboardRemove())
    return EDITURL


def edit_url(update: Update, context: CallbackContext):
    photographer: Photographer = context.user_data['edit_grapher']
    url = update.message.text
    if url == '/salta':
        url = ""
    return param_switcher(update, context, photographer, 'url', url, 'il link al tuo sito web')


def edit_ig_switch(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Ok invia il nuovo username del tuo profilo instagram.\nUtilizza il formato '@username'.\n"
        "Se vuoi rimuovere il tuo profilo instagram usa il comando /salta",
        reply_markup=ReplyKeyboardRemove())
    return EDITIG


def edit_ig(update: Update, context: CallbackContext):
    photographer: Photographer = context.user_data['edit_grapher']
    insta = update.message.text
    if insta == '/salta':
        return param_switcher(update, context, photographer, 'ig', "", 'il profilo instagram')
    elif validate_ig_username(insta[1:]):
        return param_switcher(update, context, photographer, 'ig', insta[1:], 'il profilo instagram')
    else:
        update.message.reply_text("Sembra che non ci sia nessun profilo associato a questo username!\n"
                                  "Ricontrolla e rimandamelo oppure usa il comando /salta")
        return EDITIG


def param_switcher(update: Update, context: CallbackContext, fotografo: Photographer, choiche: str, new_value: str,
                   to_write: str):
    gra_logger.info(extra=extra, msg=f"Request param_switcher. choiche: {choiche}, new_value: {new_value}")
    switcher = {
        'nome': 'name',
        'url': 'website',
        'ig': 'instagram'
    }

    try:
        setattr(fotografo, switcher[choiche], new_value)
        fotografo.save()
        update_and_show(update.message, context, fotografo, 'photographers', 'owner')
    except Exception as E:
        update.message.reply_text(f'C\'è stato un errore durante la modifica {to_write}',
                                  reply_markup=ReplyKeyboardRemove())
        gra_logger.error(extra=extra, msg=f"Errore {E}")
    return ConversationHandler.END


edit_grapher_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_grapher_callback_handler, pattern='^(EDIT_GRAPHER)$')],

    states={
        WHATTOEDIT: [MessageHandler(Filters.text(editable), what_to_edit)],
        EDITNAME: [MessageHandler(Filters.text & (~Filters.command), edit_name)],
        EDITURL: [MessageHandler(Filters.entity("url"), edit_url), CommandHandler("salta", edit_url)],
        EDITIG: [MessageHandler(Filters.entity(MessageEntity.MENTION), edit_ig), CommandHandler("salta", edit_ig)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
