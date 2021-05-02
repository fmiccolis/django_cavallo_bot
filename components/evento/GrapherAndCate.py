from telegram import ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext

from botLogger import logger as eve_logger
from components.navigation import init_navigation
from botConfig import cancel, CONV_TIMEOUT
from core.models import Photographer, Category

SEARCHTYPE, DEEPSEARCH = range(2)

extra = {'file_name': 'GrapherAndCate.py'}


def eventi(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request eventi")
    message = update.message
    keyboard = [['ricerca per fotografo'], ['ricerca per categoria']]
    message.reply_text("Benvenuto nella ricerca degli eventi\.\nPer prima cosa scegli come vuoi cercare gli "
                       "eventi\.\nLe due opzioni disponibili sono *fotografo* e *categoria*\.\n\nCome avrai "
                       "già intuito le due ricerca ti permettono di visualizzare tutti gli eventi di un "
                       "fotografo oppure tutti gli eventi con una determinata categoria\.",
                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard, one_time_keyboard=True),
                       parse_mode=ParseMode.MARKDOWN_V2)
    return SEARCHTYPE


def search_by_grapher(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request search_by_grapher")
    message = update.message
    message.reply_text(
        "Puoi ottimizzare la ricerca inviandomi il nome o una parte del nome di un fotografo!\n"
        "Se non conosci il nome usa il comando /salta e ti invierò tutti i fotografi"
    )
    return DEEPSEARCH


def deepsearch(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request deepsearch")
    message = update.message
    nome = message.text
    if nome == "/salta":
        fotografi = Photographer.objects.filter(events__status=True).distinct()
        deftext = "Mi dispiace ma non ci sono fotografi che hanno degli eventi attivi!"
    else:
        fotografi = Photographer.objects.filter(name=nome, events__status=True)
        deftext = "Non ci sono fotografi con quel nome con eventi attivi"
    if fotografi:
        message.reply_text(f"Ecco qui!\nHo trovato {len(fotografi)} fotografo/i", reply_markup=ReplyKeyboardRemove())
        init_navigation(message, context, list(fotografi), 'photographers', 'viewer')
        context.user_data['search_choiche'] = 'fotografo'
        context.user_data['fotografo_id'] = fotografi[0]
    else:
        message.reply_text(deftext, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def search_by_cate(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request search_by_cate")
    message = update.message
    categorie = Category.objects.filter(events__status=True)
    if categorie:
        message.reply_text(f"Ecco qui!\nHo trovato {len(categorie)} categoria/e", reply_markup=ReplyKeyboardRemove())
        init_navigation(message, context, list(categorie), 'categories', 'viewer')
        context.user_data['categoria'] = categorie[0]
        context.user_data['search_choiche'] = 'categoria'
    else:
        message.reply_text(
            "Mi dispiace ma non ci sono categorie che hanno degli eventi attivi!",
            reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


show_all_event_conv = ConversationHandler(
    entry_points=[CommandHandler('eventi', eventi)],

    states={
        SEARCHTYPE: [
            MessageHandler(Filters.regex(r'fotografo'), search_by_grapher),
            MessageHandler(Filters.regex(r'categoria'), search_by_cate)
        ],
        DEEPSEARCH: [MessageHandler(Filters.text, deepsearch)]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
