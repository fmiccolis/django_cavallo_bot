import emoji
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext)

from botLogger import logger as cat_logger
from components.navigation import init_navigation
from botConfig import cancel, all_emojis, CONV_TIMEOUT, dev_restricted
from core.models import Category

CREATION, ADDNAME, ADDEMO, ADDDESC = range(4)

extra = {'file_name': 'AddNewCategory.py'}


@dev_restricted
def categorie(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = update.effective_message
    cat_logger.info(extra=extra, msg=f"Request categorie. dev_id: {user_id}")
    reply_keyboard = [['aggiungi', 'termina']]
    categories = Category.objects.all()
    if len(categories) == 0:
        message.reply_text("Non sono state aggiunte ancora le categorie. Usa il pulsante \'aggiungi\' per creare "
                           "una nuova categoria")
        return CREATION
    message.reply_text(f'Ciao, ci sono {len(categories)} categorie salvate nel sistema.\n\n')
    context.user_data['categoria'] = categories[0]
    init_navigation(message, context, list(categories), 'categories', 'devs')
    message.reply_text('Tramite i pulsanti sotto i messaggi scegli se disabilitare le categorie\n'
                       'Se vuoi aggiungere nuove categorie clicca nella testiera \'aggiungi\'',
                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=reply_keyboard, one_time_keyboard=True))
    return CREATION


@dev_restricted
def aggiungi(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = update.effective_message
    cat_logger.info(extra=extra, msg=f"Request aggiungi. dev_id: {user_id}")
    message.reply_text("Molto bene!\nPer prima cosa ho bisogno del nome di questa categoria",
                       reply_markup=ReplyKeyboardRemove())
    return ADDNAME


@dev_restricted
def addname(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = update.effective_message
    cat_name = message.text
    cat_logger.info(extra=extra, msg=f"Request addname. New Category name: {cat_name} dev_id: {user_id}")
    context.user_data['category_name'] = cat_name
    message.reply_text('Molto bene, adesso scegli un emoji da assegnare a questa categoria')
    return ADDEMO


@dev_restricted
def addemo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = update.effective_message
    cate_emoji = emoji.demojize(message.text)
    cat_logger.info(extra=extra, msg=f"Request addemo. New Category name: {cate_emoji} dev_id: {user_id}")
    context.user_data['category_emoji'] = cate_emoji
    message.reply_text('Molto bene, adesso ho solo bisogno della desccrizione da dare a questa categoria')
    return ADDDESC


@dev_restricted
def adddesc(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = update.effective_message
    cate_desc = message.text
    cate_name = context.user_data['category_name']
    cate_emoji = context.user_data['category_emoji']
    cat_logger.info(extra=extra, msg=f"Request adddesc. New Category desc: {cate_desc} dev_id: {user_id}")
    category = {
        'name': cate_name,
        'emoji': cate_emoji,
        'description': cate_desc
    }
    try:
        db_category = Category(**category)
        db_category.save()
        message.reply_text('Perfetto!\nHo salvato la nuova categoria. Sarà disponibile come '
                           'opzione nei prossimi eventi.')
    except Exception as E:
        message.reply_text('Errore durante il salvataggio della nuova categoria.')
        cat_logger.error(extra=extra, msg=f"Errore {E}")
    return ConversationHandler.END


add_new_category = ConversationHandler(
    entry_points=[CommandHandler("categorie", categorie)],

    states={
        CREATION: [MessageHandler(Filters.regex('^(aggiungi)$'), aggiungi),
                   MessageHandler(Filters.regex('^(termina)$'), cancel)],

        ADDNAME: [MessageHandler(Filters.text & (~Filters.command), addname)],

        ADDEMO: [MessageHandler(Filters.text(all_emojis), addemo)],

        ADDDESC: [MessageHandler(Filters.text & (~Filters.command), adddesc)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
