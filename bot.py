# general python import
import json

# specific telegram bot import

from telegram import ParseMode, Update, User
from telegram.ext import Updater, CommandHandler, CallbackContext

# custom user import
from botConfig import devs, TOKEN, boterror
from botLogger import logger as bot_logger
# components import
from components.categoria import add_new_category, edit_category_conv, toggle_category_hand, remove_category_conv
from components.evento import add_new_event, toggle_event_hand, token_message_conv, get_events_conv, remove_event_conv, \
    edit_event_conv, show_all_event_conv, single_event_conv
from components.fotografo import create_new_photographer, confirm_photographer, remove_grapher_conv, \
    toggle_grapher_hand, edit_grapher_conv
from components.telegram_user import send_user_video, remove_video_conv, edit_video_conv
from components.photomatch import find_face_conv, restart_scan_conv, toggle_match_conv
from components.navigation import first_element_hand, prev_element_hand, next_element_hand, last_element_hand, \
    this_element_hand
from core.models import TelegramUser, Photographer

extra = {'file_name': 'bot.py'}


def start(update: Update, context: CallbackContext):
    user: User = update.effective_user
    try:
        tg_user = TelegramUser.objects.get(pk=user.id)
        parameter = "Bentornato " + tg_user.first_name
        bot_logger.info(extra=extra, msg=f"{tg_user.id} already exist")
    except Exception as E:
        parameter = "Benvenuto " + user.first_name
        bot_logger.info(extra=extra, msg=f"{user.id} not saved")
        try:
            bot_logger.info(extra=extra, msg=user.to_dict())
            tg_user = TelegramUser(**TelegramUser.generate_constructor(user=user.to_dict()))
            tg_user.save()
            bot_logger.info(extra=extra, msg=f"{tg_user.id} saved")
        except Exception as E:
            bot_logger.error(extra=extra, msg=f"Il nuovo utente non è stato salvato. user_id: {user.id}")
            bot_logger.error(extra=extra, msg=f"Errore: {E}")

    update.message.reply_text(
        f"{parameter}! Il mio nome è Cavallo Production bot.\n"
        f"Se hai partecipato ad un compleanno targato Cavallo Production, trovare le tue foto "
        f"fra quelle della festa sarà ancora più semplice!\nClicca su /invia per registare un video.\n"
        f"Clicca su /help per avere una lista completa dei comandi.\n"
        f"Clicca su /cancel per annullare l\'operazione corrente."
    )


def show_commands(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    strbuilder = 'Ecco la lista completa dei comandi attivi nel Bot:\n\n' \
                 '*Comandi Generici*\n'
    with open('commands.json') as json_file:
        data = json.load(json_file)
        for command in data['normal']:
            strbuilder += f'/{command["command"]} \- {command["description"]}\n'
        tg_user = TelegramUser.objects.get(pk=user_id)
        is_photographer = Photographer.objects.filter(telegram_user=tg_user).count() > 0
        if is_photographer:
            strbuilder += f'\n*Comandi per fotografi*\n'
            for command in data['photographer']:
                strbuilder += f'/{command["command"]} \- {command["description"]}\n'
        if user_id in devs:
            strbuilder += f'\n*Comandi per sviluppatori*\n'
            for command in data['dev']:
                strbuilder += f'/{command["command"]} \- {command["description"]}\n'
    update.message.reply_text(strbuilder, parse_mode=ParseMode.MARKDOWN_V2)


def test(update: Update, context: CallbackContext):
    print(update)
    file_zip = update.message.document
    file_zip.get_file().download()
    print(file_zip.get_file())


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # ,request_kwargs={'read_timeout': 8, 'connect_timeout': 9} riga da aggiungere se ci sono errori durante la ricerca
    updater = Updater(
        TOKEN,
        use_context=True,
        # base_url='http://localhost:8081/bot',
        # base_file_url='http://localhost:8081/file/bot'
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # dp.add_handler(MessageHandler(Filters.document.zip, test))

    # comando start per avviare il bot la prima volta
    dp.add_handler(CommandHandler("start", start))

    # comando help per ottenere la lista dei comandi censiti
    dp.add_handler(CommandHandler("help", show_commands))

    # comando fotografi per ottenere la lista dei fotografi censiti
    dp.add_handler(confirm_photographer)

    # conversazione per rimuovere per sempre un evento
    dp.add_handler(remove_event_conv, group=1)

    # conversazione per rimuovere per sempre un fotografo
    dp.add_handler(remove_grapher_conv, group=1)

    # conversazione per rimuovere per sempre una categoria
    dp.add_handler(remove_category_conv, group=1)

    # conversazione per rimuovere i dati del volto di un utente
    dp.add_handler(remove_video_conv, group=1)

    # conversazione per attivare disattivare un evento
    dp.add_handler(toggle_event_hand, group=1)

    # conversazione per attivare disattivare un fotografo
    dp.add_handler(toggle_grapher_hand, group=1)

    # conversazione per attivare disattivare una categoria
    dp.add_handler(toggle_category_hand, group=1)

    # conversazione per mandare all'utente il video che ha caricato
    dp.add_handler(send_user_video)

    # conversazione per modificare i dati di un evento
    dp.add_handler(edit_event_conv, group=1)

    # conversazione per modificare i dati di un fotografo
    dp.add_handler(edit_grapher_conv, group=1)

    # conversazione per modificare i dati di una categoria
    dp.add_handler(edit_category_conv, group=1)

    # conversazione per rifare lo scanning del sito di un evento
    dp.add_handler(restart_scan_conv, group=1)

    # conversazione per ottenere tutti gli eventi dato un fotografo o una categoria
    dp.add_handler(get_events_conv)

    # conversazione per modificare i dati del volto di un utente
    dp.add_handler(edit_video_conv, group=1)

    # conversazione per mostrare fotografi e categorie da scegliere per poi ottenere gli eventi
    dp.add_handler(show_all_event_conv)

    # conversazione per candidarsi come nuovo fotografo
    dp.add_handler(create_new_photographer)

    # conversazione per aggiungere una nuova categoria
    dp.add_handler(add_new_category)

    # conversazione per cercare il volto di un utente nelle foto di un evento
    dp.add_handler(find_face_conv, group=1)

    # conversazione per confermare o meno il match di una foto
    dp.add_handler(toggle_match_conv, group=1)

    # conversazione per aggiungere un nuovo evento
    dp.add_handler(add_new_event)

    # conversazione per mostrare un singolo evento partendo dal token
    dp.add_handler(single_event_conv)

    # conversazione per mostrare il messaggio token da inoltrare
    dp.add_handler(token_message_conv, group=1)

    # navigation: primo elemento
    dp.add_handler(first_element_hand)

    # navigation: elemento precedente
    dp.add_handler(prev_element_hand)

    # navigation: elemento corrente
    dp.add_handler(this_element_hand)

    # navigation: elemento successivo
    dp.add_handler(next_element_hand)

    # navigation: ultimo elemento
    dp.add_handler(last_element_hand)

    # log all errors
    dp.add_error_handler(boterror)

    # Start the Bot
    bot_logger.info(extra=extra, msg="Bot started")
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    # Start the Bot
    bot_logger.info(extra=extra, msg="Bot stopped")


if __name__ == '__main__':
    main()
    # dir -Recurse *.py | Get-Content | Measure-Object -Line 4138
