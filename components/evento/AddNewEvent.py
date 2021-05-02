import locale
import os
import re
import threading
from datetime import datetime
from time import sleep

import emoji
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, Update)
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext)

from botLogger import logger as eve_logger
from components import utilities
from components.navigation import init_navigation
from components.utilities import download_and_extract_zip
from botConfig import get_year_keyboard, get_month_keyboard, months, get_days_by_month_and_year, \
    create_dir, EVENTS_PATH, template_token_msg, EVENT_ZIP_PATH, cancel, CONV_TIMEOUT
from core.models import Category, TelegramUser, Photographer, Event

CHOICHE, ADDNAME, ADDDESC, ADDURL, ADDCAT, ADDYEAR, ADDMONTH, ADDDAY, ISPUBLIC, STARTSCANNING = range(10)
categories = Category.objects.filter(status=True)
locale.setlocale(0, "it")

extra = {'file_name': 'AddNewEvent.py'}


def event_manager(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request event_manager")
    message = update.message
    user_id = message.from_user.id
    tg_user = TelegramUser.objects.get(pk=user_id)
    try:
        fotografo = Photographer.objects.get(telegram_user=tg_user)
    except Photographer.DoesNotExist as DNE:
        eve_logger.critical(extra=extra, msg=f"Request event_manager. {DNE}")
        message.reply_text("Non capisco cosa tu mi voglia dire")
        return ConversationHandler.END

    if len(categories) == 0:
        eve_logger.critical(extra=extra, msg=f"Request event_manager. There are no categories")
        message.reply_text("Non sono state censite le categorie, non puoi ancora creare i tuoi eventi, mi dispiace!")
        return ConversationHandler.END

    eve_logger.info(extra=extra, msg=f"Request event_manager. {fotografo.name} enter the event manager")
    if fotografo.status:
        keyboard_action = [
            ["Crea un nuovo evento", "Mostra tutti gli eventi"],
            ["Gestisci i tuoi dati"]
        ]
        message.reply_text(f"Benvenuto {fotografo.name} nella sezione a te dedicata per la gestione "
                           f"dei tuoi eventi!\nUsa i pulsanti qui sotto per creare o gestire un evento",
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_action,
                                                            one_time_keyboard=True))
        context.user_data["fotografo"] = fotografo
        context.user_data["remaining_space"] = fotografo.disk_space
        return CHOICHE
    else:
        eve_logger.critical(extra=extra, msg=f"Request event_manager. {fotografo.name} is not enabled")
        message.reply_text("Il tuo profilo non è stato ancora abilitato come fotografo, "
                           "attendi fino aquando non sarai contattato per l\'attivazione.")


def create(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request create")
    update.message.reply_text("Ok per prima cosa scegli un nome per l\'evento.",
                              reply_markup=ReplyKeyboardRemove())
    return ADDNAME


def add_event_name(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request add_event_name. name: {update.message.text}")
    context.user_data['nome_comando'] = update.message.text
    update.message.reply_text("Ora mi serve una descrizione.\nScrivi quello che vuoi usando poche parole.\n\n"
                              "Puoi saltare questo passaggio usando il comando /salta")
    return ADDDESC


def add_event_desc(update: Update, context: CallbackContext):
    message = update.message
    eve_logger.info(extra=extra, msg=f"Request add_event_desc. desc: {message.text}")
    context.user_data['descrizione'] = message.text
    remaining_space = context.user_data['remaining_space']
    if message.text == '/salta':
        context.user_data['descrizione'] = ""
    message.reply_text(
        "Bene, adesso una parte molto importante!\n"
        "Ho bisogno del link url alla pagina del tuo sito internet dove è salvato l\'album "
        "delle foto dell\'evento.\nQuesta parte è importante perchè in automatico al salvataggio "
        "dell\'evento andrò a cercare e scaricare tutte le foto.\nSfrutta la funzione copia e "
        "incolla del tuo cellulare per evitare qualsiasi errore!"
    )
    message.reply_text(
        f"Hai comunque un\'altra possibilità e cioè quella di inviarmi uno zip contenente le foto dell\'evento.\n"
        f"Questa opzione è gratuita fino ad un massimo di 500MB. Poi se vorrai inserire un nuovo evento utilizzando "
        f"lo zip pagherai soltanto 0,50€ per ogni nuovo GB.\n\nIl tuo spazio rimanente è {remaining_space} MB"
    )
    return ADDURL


def add_url_or_zip(update: Update, context: CallbackContext):
    message = update.message
    remaining_space = context.user_data['remaining_space']
    file_zip = message.document
    if file_zip:
        eve_logger.info(extra=extra, msg=f"Request add_url_or_zip. path: {file_zip.file_name}")
        if round(file_zip.file_size / 1000000) > remaining_space:
            message.reply_text("Il file che hai appena inviato supera lo spazio rimanente a te dedicato!\n"
                               "Invia un nuovo file zip oppure mandami l\'url al sito dell\'album")
            return ADDURL
        context.user_data['url_location'] = 'internal'
        context.user_data['zip_name'] = file_zip.file_name
        context.user_data['zip_size'] = round(file_zip.file_size / 1000000)
        x = threading.Thread(target=download_and_extract_zip, args=(update, context,))
        x.start()
        message.reply_text("Inizio a scaricare il file zip che mi hai appena inviato.\n"
                           "Nel frattempo continuiamo.\n\n"
                           "(Ti invio un messaggio quando finisce il download)")
    else:
        eve_logger.info(extra=extra, msg=f"Request add_url_or_zip. url: {message.text}")
        context.user_data['url_location'] = 'external'
        context.user_data['url'] = message.text
    keyboard_category = list()
    this_line = list()
    for category in categories:
        if len(this_line) >= 2:
            keyboard_category.append(this_line.copy())
            this_line.clear()
        this_line.append(f"{category.name} {emoji.emojize(category.emoji)}")
    keyboard_category.append(this_line.copy())
    message.reply_text("Adesso devi scegliere la categoria fra quelle salvate e abilitate.",
                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_category,
                                                        one_time_keyboard=True))
    return ADDCAT


def add_cat(update: Update, context: CallbackContext):
    message = update.message
    eve_logger.info(extra=extra, msg=f"Request add_cat. category: {message.text}")
    category_name = message.text.split()[0]
    category: Category = Category.objects.filter(name=category_name)[0]
    if category is None:
        message.reply_text("C\'è stato un errore nel trovare la categoria, ripristinerò subito la situazione")
        return ConversationHandler.END

    context.user_data['cat'] = category
    keyboard_years = get_year_keyboard()
    message.reply_text("Ok per ultima cosa ho bisogno di sapere quando si è svolto l\'evento.\n"
                       "Sarà più semplice per i tuoi utenti cercare e trovate ciò che stanno cercando!\n\n"
                       "Per prima cosa scegli l\'anno",
                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_years,
                                                        one_time_keyboard=True))
    return ADDYEAR


def add_year(update: Update, context: CallbackContext):
    year = update.message.text
    eve_logger.info(extra=extra, msg=f"Request add_year. year: {year}")
    context.user_data['year'] = year
    update.message.reply_text("Adesso scegli il mese",
                              reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=get_month_keyboard(year),
                                                               one_time_keyboard=True))
    return ADDMONTH


def add_month(update: Update, context: CallbackContext):
    message = update.message
    month = message.text
    eve_logger.info(extra=extra, msg=f"Request add_month. month: {month}")
    month_num = months.index(month) + 1
    context.user_data['month'] = month_num
    year = int(context.user_data['year'])
    keyboard_days = get_days_by_month_and_year(month_num, year)
    message.reply_text("Infine scegli il giorno",
                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_days,
                                                        one_time_keyboard=True))
    return ADDDAY


def add_day(update: Update, context: CallbackContext):
    message = update.message
    day = message.text
    eve_logger.info(extra=extra, msg=f"Request add_day. day: {day}")
    context.user_data['day'] = day
    keyboard_yes_no = [['Si'], ['No']]
    message.reply_text(
        "L\'evento sarà pubblico?\n\n"
        "Questa informazione mi serve per sapere se un utente potrà cercare l\'evento anche senza usare il token",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_yes_no, one_time_keyboard=True)
    )
    return ISPUBLIC


def yes_is_public(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request yes_is_public")
    context.user_data['public'] = True
    return save(update, context)


def not_public(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request not_public")
    context.user_data['public'] = False
    return save(update, context)


def save(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request save")
    message = update.message
    url_location = context.user_data.get('url_location', None)
    movezip = False
    server_file = None
    if url_location == 'internal':
        eve_logger.info(extra=extra, msg=f"Request save. local url")
        text_template = "prima di procedere al salvataggio dell\'evento devo controllare che il file " \
                        "zip sia stato scaricato.\n\nAttendi... {0}"
        progress_circle = ["╚", "╔", "╗", "╝"]
        progress_level = 0
        wait_msg = message.reply_text(text_template.format(progress_circle[progress_level]))
        while True:
            server_file = context.user_data.get('url', None)
            if server_file:
                movezip = True
                url = ""
                break
            else:
                progress_level += 1
                if progress_level == 4:
                    progress_level = 0
                wait_msg.edit_text(text_template.format(progress_circle[progress_level]))
                sleep(1)
        wait_msg.edit_text(f"Bene il file è stato scaricato correttamente")
    else:
        eve_logger.info(extra=extra, msg=f"Request save. external link")
        url = context.user_data['url']

    fotografo: Photographer = context.user_data['fotografo']
    nome_comando = context.user_data['nome_comando']
    descrizione = context.user_data['descrizione']
    cat: Category = context.user_data['cat']
    year = int(context.user_data['year'])
    month = int(context.user_data['month'])
    day = int(context.user_data['day'])
    public = bool(context.user_data['public'])
    date = datetime(year, month, day)
    try:
        event = Event(
            name=nome_comando,
            description=descrizione,
            url=url,
            photographer=fotografo,
            category=cat,
            is_public=public,
            date=date
        )
        event.save()

        create_dir([
            os.path.join(EVENTS_PATH, str(event.id)),
            EVENT_ZIP_PATH.format(event.id)
        ])

        context.user_data["evento"] = event

        if movezip:
            final_path = os.path.join(EVENT_ZIP_PATH.format(event.id), context.user_data['zip_name'])
            server_file.download(final_path)
            event.url = final_path
            event.save()
            context.user_data["evento"] = event
            remaining_space = context.user_data['remaining_space']
            zip_size = context.user_data['zip_size']
            fotografo.disk_space = remaining_space - zip_size
            fotografo.save()

        reply_keyboard = [['Si', 'No']]
        message.reply_text(
            "Ottimo, ho salvato il tuo evento!\n\n"
            "Ho generato un token che gli utenti potranno usare per trovare più facilmente questo evento!\n"
            "Qui sotto riceverai un messaggio che potrai direttamente inoltrare a tutti gli invitati all\'evento!",
            reply_markup=ReplyKeyboardRemove()
        )
        message.reply_text(
            template_token_msg.format(nome_comando=nome_comando, token=event.code, context=context),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.HTML
        )
        message.reply_text(
            "Se mi dai il via inizierò a cercare tutte le foto dal link che mi hai passato e "
            "estrarrò tutte i volti.",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=reply_keyboard, one_time_keyboard=True))
        return STARTSCANNING
    except Exception as E:
        message.reply_text("C\'é stato un errore nel salvataggio dell\'evento!")
        eve_logger.error(extra=extra, msg=f"Error {E}")
        return ConversationHandler.END


def end_conv(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request end_conv")
    update.message.reply_text(
        "Ok, alla prossima\!\nRicorda che per tornare in questa sezione devi inserire il "
        "comando /gestione _password_", parse_mode=ParseMode.MARKDOWN_V2)
    return ConversationHandler.END


def show_all_event(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request show_all_event")
    message = update.message
    fotografo: Photographer = context.user_data['fotografo']
    eventi = Event.objects.filter(photographer=fotografo)
    if len(eventi) == 0:
        message.reply_text("Non hai ancora caricato eventi, reinsiresci il comando /gestione "
                           "la tua password e procedi con \'Crea un nuovo evento\'", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    eve_logger.info(extra=extra, msg=f"Request show_all_event. total events {len(eventi)}")

    message.reply_text("Ecco la lista degli eventi", reply_markup=ReplyKeyboardRemove())
    init_navigation(message, context, list(eventi), 'events', 'owner')
    context.user_data['evento'] = eventi[0]
    return ConversationHandler.END


def manage_info(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request manage_info")
    fotografo: Photographer = context.user_data["fotografo"]
    init_navigation(update.message, context, [fotografo], 'photographers', 'owner')
    return ConversationHandler.END


add_new_event = ConversationHandler(
    entry_points=[CommandHandler('gestione', event_manager)],

    states={
        CHOICHE: [
            MessageHandler(Filters.regex(r'nuovo'), create),
            MessageHandler(Filters.regex(r'tutti'), show_all_event),
            MessageHandler(Filters.regex(r'Gestisci'), manage_info)
        ],
        ADDNAME: [MessageHandler(Filters.text & (~Filters.command), add_event_name)],
        ADDDESC: [MessageHandler(Filters.text, add_event_desc),
                  CommandHandler("salta", add_event_desc)],
        ADDURL: [MessageHandler(Filters.entity("url"), add_url_or_zip),
                 MessageHandler(Filters.document.zip, add_url_or_zip)],
        ADDCAT: [MessageHandler(Filters.text(
            [category.name + ' ' + emoji.emojize(category.emoji) for category in categories]
        ), add_cat)],
        ADDYEAR: [MessageHandler(Filters.regex(re.compile(r'^([\s\d]+)$')), add_year)],
        ADDMONTH: [MessageHandler(Filters.text(months), add_month)],
        ADDDAY: [MessageHandler(Filters.regex(re.compile(r'^([\s\d]+)$')), add_day)],
        ISPUBLIC: [MessageHandler(Filters.regex('^(Si)$'), yes_is_public),
                   MessageHandler(Filters.regex('^(No)$'), not_public)],
        STARTSCANNING: [MessageHandler(Filters.regex('^(Si)$'), utilities.start_scanning),
                        MessageHandler(Filters.regex('^(No)$'), end_conv)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
