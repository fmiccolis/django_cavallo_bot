import re
from datetime import datetime

import emoji
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, Update)
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from botLogger import logger as eve_logger
from components.evento.EventUtil import update_and_show
from botConfig import get_year_keyboard, get_month_keyboard, months, get_days_by_month_and_year, \
    template_token_msg, cancel, CONV_TIMEOUT
from core.models import Category, Event, event_code

WHATTOEDIT, EDITNAME, EDITDESC, EDITURL, EDITCAT, EDITYEAR, EDITMONTH, EDITDAY = range(8)
active_categories = Category.objects.filter(status=True)
editable = ['nome', 'descrizione', 'url', 'categoria', 'data', 'visibilità', 'token']

extra = {'file_name': 'EditEvent.py'}


def edit_event_callback_handler(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request event_manager")
    query = update.callback_query
    query.answer()
    message = query.message
    msgid = message.message_id
    editable_keyboard = [[column] for column in editable]
    message.reply_text(
        "Ok scegli quale parametro modificare per il tuo evento",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=editable_keyboard, one_time_keyboard=True)
    )
    message.delete()
    evento: Event = context.user_data['evento']
    eve_logger.info(evento)
    context.user_data['msg_to_delete'] = msgid
    context.user_data["remaining_space"] = evento.photographer.disk_space
    return WHATTOEDIT


def what_to_edit(update: Update, context: CallbackContext):
    swithcer = {
        'nome': edit_name_switch,
        'descrizione': edit_desc_switch,
        'url': edit_url_switch,
        'categoria': edit_cat_switch,
        'data': edit_data_switch,
        'visibilità': edit_vis,
        'token': edit_token,
    }
    eve_logger.info(extra=extra, msg=f"Request what_to_edit. edit: {update.message.text}")
    return swithcer[update.message.text](update, context)


def edit_name_switch(update: Update, context: CallbackContext):
    update.message.reply_text("Ok scegli il nuovo nome per l'evento", reply_markup=ReplyKeyboardRemove())
    return EDITNAME


def edit_name(update: Update, context: CallbackContext):
    return param_switcher(update, context, 'name', update.message.text, 'il nome')


def edit_desc_switch(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Ok scegli la nuova descrizione per l'evento oppure usa il comando /salta per cancellare la precendente",
        reply_markup=ReplyKeyboardRemove()
    )
    return EDITDESC


def edit_desc(update: Update, context: CallbackContext):
    new_desc = update.message.text
    if new_desc == '/salta':
        new_desc = ''
    return param_switcher(update, context, 'description', new_desc, 'la descrizione')


def edit_url_switch(update: Update, context: CallbackContext):
    remaining_space = context.user_data["remaining_space"]
    update.message.reply_text("Ok scegli il nuovo url per l'evento.\nTi ricordo di sfruttare la funzione "
                              "copia e incolla del tuo smartphone o pc per essere sicuro di inserire un link valido",
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        f"Hai comunque un\'altra possibilità e cioè quella di inviarmi uno zip contenente le foto dell\'evento.\n"
        f"Questa opzione è gratuita fino ad un massimo di 500MB. Poi se vorrai inserire un nuovo evento utilizzando "
        f"lo zip pagherai soltanto 0,50€ per ogni nuovo GB.\n\nIl tuo spazio rimanente è {remaining_space} MB"
    )
    return EDITURL


def edit_url_or_zip(update: Update, context: CallbackContext):
    return param_switcher(update, context, 'url', update.message.text, 'il link all\'album')


def edit_cat_switch(update: Update, context: CallbackContext):
    keyboard_cate = list()
    this_line = list()
    for cat in active_categories:
        if len(this_line) >= 2:
            keyboard_cate.append(this_line.copy())
            this_line.clear()
        this_line.append(f"{cat.name} {emoji.emojize(cat.emoji)}")
    keyboard_cate.append(this_line.copy())
    update.message.reply_text(
        "Ok scegli la nuova categoria per l'evento per l'evento fra quelle qui sotto disponibili",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_cate, one_time_keyboard=True))
    return EDITCAT


def edit_cat(update: Update, context: CallbackContext):
    category_name = update.message.text.split()[0]
    category = Category.objects.filter(name=category_name)
    return param_switcher(update, context, 'category', category, 'la categoria')


def edit_data_switch(update: Update, context: CallbackContext):
    keyboard_years = get_year_keyboard()
    update.message.reply_text("Ok per scegliere la nuova data dell\'evento bisogna partire dall\'anno.\n"
                              "Scegli il nuovo anno",
                              reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_years,
                                                               one_time_keyboard=True))
    return EDITYEAR


def edit_year(update: Update, context: CallbackContext):
    year = update.message.text
    context.user_data['year'] = year
    update.message.reply_text("Adesso scegli il mese",
                              reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=get_month_keyboard(year),
                                                               one_time_keyboard=True))
    return EDITMONTH


def edit_month(update: Update, context: CallbackContext):
    month = update.message.text
    month_num = months.index(month) + 1
    context.user_data['month'] = month_num
    year = int(context.user_data['year'])
    keyboard_days = get_days_by_month_and_year(month_num, year)
    update.message.reply_text("Infine scegli il giorno",
                              reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_days,
                                                               one_time_keyboard=True))
    return EDITDAY


def edit_day(update: Update, context: CallbackContext):
    year = int(context.user_data['year'])
    month = int(context.user_data['month'])
    day = int(update.message.text)
    date = datetime(year, month, day)
    return param_switcher(update, context, 'date', date, 'la data')


def edit_vis(update: Update, context: CallbackContext):
    evento: Event = context.user_data['evento']
    private = "Privato :lock:"
    public = "Pubblico :busts_in_silhouette:"
    if evento.is_public:
        new_visibility = f"{private}\t:arrow_right:\t{public}"
        last_msg = f"Adesso l\'evento sarà visibile anche *senza* l\'utilizzo del token"
    else:
        new_visibility = f"{public}\t:arrow_right:\t{private}"
        last_msg = f"Adesso l\'evento sarà visibile *solo* con l\'utilizzo del token"
    update.message.reply_text(
        f"Molto bene\. La visibilità passerà da\n\n"
        f"{emoji.emojize(new_visibility, use_aliases=True)}\n\n"
        f"{last_msg}",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return param_switcher(update, context, 'is_public', not evento.is_public, 'la visibilità')


def edit_token(update: Update, context: CallbackContext):
    evento: Event = context.user_data['evento']
    newtoken = event_code()
    update.message.reply_text(
        "Ho generato il nuovo token!\nAddesso ti invio un messaggio che potrai inoltrare "
        "a tutti gli invitati a questo evento",
        reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_text(
        template_token_msg.format(nome_comando=evento.name, token=newtoken, context=context),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML
    )
    return param_switcher(update, context, 'code', newtoken, 'il token')


def param_switcher(update: Update, context: CallbackContext, choiche: str, new_value, to_write: str):
    eve_logger.info(extra=extra, msg=f"Request param_switcher. choiche: {choiche} new_value: {new_value}")
    try:
        evento: Event = context.user_data['evento']
        setattr(evento, choiche, new_value)
        evento.save()
        update_and_show(update.message, context, evento)
    except Exception as E:
        eve_logger.error(f"Errore: {E}")
        msg_text = f'C\'è stato un errore durante la modifica {to_write}'
        update.message.reply_text(msg_text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


edit_event_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_event_callback_handler, pattern='^(EDIT_EVENT)$')],

    states={
        WHATTOEDIT: [MessageHandler(Filters.text(editable), what_to_edit)],
        EDITNAME: [MessageHandler(Filters.text & (~Filters.command), edit_name)],
        EDITDESC: [MessageHandler(Filters.text, edit_desc), CommandHandler('salta', edit_desc)],
        EDITURL: [MessageHandler(Filters.entity("url"), edit_url_or_zip),
                  MessageHandler(Filters.document.zip, edit_url_or_zip)],
        EDITCAT: [MessageHandler(Filters.text(
            [category.name + ' ' + emoji.emojize(category.emoji) for category in active_categories]
        ), edit_cat)],
        EDITYEAR: [MessageHandler(Filters.regex(re.compile(r'^([\s\d]+)$')), edit_year)],
        EDITMONTH: [MessageHandler(Filters.text(months), edit_month)],
        EDITDAY: [MessageHandler(Filters.regex(re.compile(r'^([\s\d]+)$')), edit_day)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
