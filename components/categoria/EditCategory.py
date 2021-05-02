import emoji
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, CommandHandler, \
    CallbackContext

from botLogger import logger as cat_logger
from components.categoria.CategoryUtil import update_and_show
from botConfig import all_emojis, cancel, CONV_TIMEOUT
from core.models import Category

WHATTOEDIT, EDITNAME, EDITDESC, EDITEMOJI = range(4)
editable = ['nome', 'descrizione', 'emoji']
extra = {'file_name': 'EditCategory.py'}


def edit_category_callback_handler(update: Update, context: CallbackContext):
    cat_logger.info(extra=extra, msg=f"Request edit_category_callback_handler")
    query = update.callback_query
    query.answer()
    editable_keyboard = [[column] for column in editable]
    query.message.reply_text(
        "Ok scegli quale informazione modificare per la categoria",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=editable_keyboard, one_time_keyboard=True)
    )
    return WHATTOEDIT


def what_to_edit(update: Update, context: CallbackContext):
    swithcer = {
        'nome': edit_name_switch,
        'descrizione': edit_desc_switch,
        'emoji': edit_emoji_switch
    }
    cat_logger.info(extra=extra, msg=f"Request what_to_edit. edit: {update.message.text}")
    return swithcer[update.message.text](update, context)


def edit_name_switch(update: Update, context: CallbackContext):
    update.message.reply_text("Ok scegli il nuovo nome per la categoria", reply_markup=ReplyKeyboardRemove())
    return EDITNAME


def edit_name(update: Update, context: CallbackContext):
    return param_switcher(update, context, 'nome', update.message.text, 'il nome')


def edit_desc_switch(update: Update, context: CallbackContext):
    update.message.reply_text("Ok scegli la nuova descrizione per la categoria", reply_markup=ReplyKeyboardRemove())
    return EDITDESC


def edit_desc(update: Update, context: CallbackContext):
    return param_switcher(update, context, 'descrizione', update.message.text, 'la descrizione')


def edit_emoji_switch(update: Update, context: CallbackContext):
    update.message.reply_text("Ok scegli la nuova emoji della categoria", reply_markup=ReplyKeyboardRemove())
    return EDITEMOJI


def edit_emoji(update: Update, context: CallbackContext):
    return param_switcher(update, context, 'emoji', emoji.demojize(update.message.text), 'l\'emoji')


def param_switcher(update: Update, context: CallbackContext, choiche, new_value, to_write):
    cat_logger.info(extra=extra, msg=f"Request param_switcher. new {choiche}: {new_value}")
    categoria: Category = context.user_data['categoria']
    switcher = {
        'nome': 'name',
        'descrizione': 'description',
        'emoji': 'emoji'
    }

    try:
        setattr(categoria, switcher[choiche], new_value)
        categoria.save()
        update_and_show(update.message, context, categoria, 'categories', 'devs')
    except Exception as E:
        cat_logger.error(extra=extra, msg=f"Request param_switcher. error while saving {E}")
        update.message.reply_text(
            f'C\'è stato un errore durante la modifica {to_write}',
            reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


edit_category_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_category_callback_handler, pattern='^(EDIT_CATEGORY)$')],

    states={
        WHATTOEDIT: [MessageHandler(Filters.text(editable), what_to_edit)],
        EDITNAME: [MessageHandler(Filters.text & (~Filters.command), edit_name)],
        EDITDESC: [MessageHandler(Filters.text & (~Filters.command), edit_desc)],
        EDITEMOJI: [MessageHandler(Filters.text(all_emojis), edit_emoji)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
