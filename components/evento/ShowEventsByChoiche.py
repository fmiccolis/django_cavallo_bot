import emoji
from django.db.models import QuerySet
from telegram import Update, Message
from telegram.ext import CallbackQueryHandler, CallbackContext

from botLogger import logger as eve_logger
from components.navigation import init_navigation
from core.models import Event, Category, Photographer

extra = {'file_name': 'ShowEventsByChoiche.py'}


def get_events(update: Update, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request get_events")
    query = update.callback_query
    query.answer()
    message = query.message
    switcher = {
        'categoria': get_by_category,
        'fotografo': get_by_grapher
    }
    switcher[context.user_data['search_choiche']](message, context)


def get_by_category(message: Message, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request get_by_category")
    category: Category = context.user_data['categoria']
    eventi = Event.objects.filter(category=category, is_public=True)
    if len(eventi) > 0:
        message.reply_text(
            f"In totale gli eventi pubblici con la categoria {category.name} "
            f"{emoji.emojize(category.emoji)} sono {len(eventi)}"
        )
        return send_events(message, context, eventi)
    else:
        message.reply_text(
            f"Non ci sono eventi pubblici per la categoria {category.name} {emoji.emojize(category.emoji)}.\n"
            f"Per vedere le foto chiedi il token dell\'evento. Il token ti permette di accedere "
            f"direttamente a qualsiasi evento caricato nel bot"
        )


def get_by_grapher(message: Message, context: CallbackContext):
    eve_logger.info(extra=extra, msg=f"Request get_by_grapher")
    photographer: Photographer = context.user_data['fotografo']
    eventi = Event.objects.filter(photographer=photographer)
    if eventi:
        message.reply_text(
            f"In totale gli eventi pubblici di {photographer.name} sono {len(eventi)}"
        )
        return send_events(message, context, eventi)
    else:
        message.reply_text(
            f"Non ci sono eventi pubblici caricati da {photographer.name}.\n"
            f"Per vedere le foto chiedi il token dell\'evento. Il token ti permette di accedere "
            f"direttamente a qualsiasi evento caricato nel bot"
        )


def send_events(message: Message, context: CallbackContext, eventi: QuerySet[Event]):
    eve_logger.info(extra=extra, msg=f"Request send_events")
    init_navigation(message, context, list(eventi), 'events', 'viewer')
    context.user_data['evento'] = eventi[0]


get_events_conv = CallbackQueryHandler(get_events, pattern='^(SHOW_EVENT)$')
