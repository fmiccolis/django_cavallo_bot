import pickle

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CallbackContext

from botLogger import logger as _log
from core.models import PhotoMatch, TelegramUser

extra = {'file_name': 'ToggleMatch.py'}


def toggle_match(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    matches = context.user_data['matches_to_check']
    msgid = update.effective_message.message_id
    swithcer = {
        "NOIAMNOT": pressed_no,
        "YESIAM": pressed_yes
    }
    okbtn = InlineKeyboardButton(text="Ho salvato la tua scelta!", callback_data="OK")
    result = swithcer[query.data](matches[str(msgid)], query.from_user.id)
    if not result:
        okbtn = InlineKeyboardButton(text="Ho avuto un errore!", callback_data="SORRY")

    keyboardok = InlineKeyboardMarkup([[okbtn]])
    update.effective_message.edit_reply_markup(reply_markup=keyboardok)


def pressed_yes(match_obj: dict, user_id: int) -> bool:
    match: PhotoMatch = match_obj.get("mid", None)
    if match:
        accuracy = match.accuracy
        if accuracy < 90:
            telegram_user: TelegramUser = TelegramUser.objects.get(pk=user_id)
            if telegram_user:
                _log.info(extra=extra, msg=f"Aggiorno il dataset di {user_id} con un encoding al {accuracy}")
                url_encodings = telegram_user.url_encodings.path
                with open(url_encodings, 'rb') as f:
                    base_encodings_dataset: dict = pickle.load(f)
                base_encodings_dataset[match_obj['url']] = {
                    'location': match_obj['loc'],
                    'encoding': match_obj['enc']
                }
                with open(url_encodings, 'wb') as f:
                    pickle.dump(base_encodings_dataset, f)
                return True
            else:
                _log.error(extra=extra, msg=f"Utente con id {user_id} non trovato")
                return False
        else:
            _log.info(extra=extra, msg=f"nessun movimento. accuratezza al {accuracy}")
            return True
    else:
        _log.error(extra=extra, msg=f"Match non trovato nel messaggio")
        return False


def pressed_no(match_obj: dict, user_id: int) -> bool:
    try:
        match: PhotoMatch = match_obj.get("mid", None)
        match.status = not match.status
        match.save()
        accuracy = match.accuracy
        if accuracy > 90:
            telegram_user: TelegramUser = TelegramUser.objects.get(pk=user_id)
            if telegram_user:
                _log.info(
                    extra=extra,
                    msg=f"Aggiorno il dataset di {user_id} rimuovendo un encoding al {accuracy}"
                )
                url_encodings = telegram_user.url_encodings
                with open(url_encodings.path, 'rb') as f:
                    base_encodings_dataset: dict = pickle.load(f)
                removed = base_encodings_dataset.pop(match_obj['url'], None)
                if removed:
                    _log.info(extra=extra, msg=f"Aggiornato dataset")
                    with open(url_encodings.path, 'wb') as f:
                        pickle.dump(base_encodings_dataset, f)
                else:
                    _log.critical(extra=extra, msg=f"Url non trovato nel dataset con accuratezza al {accuracy}")
                return True
            else:
                _log.error(extra=extra, msg=f"Utente con id {user_id} non trovato")
                return False
        else:
            _log.info(extra=extra, msg=f"nessun movimento. accuratezza al {accuracy}")
            return True
    except Exception as E:
        _log.error(extra=extra, msg=f"Match id nullo. errore nel dict {E}")
        return False


toggle_match_conv = CallbackQueryHandler(toggle_match, pattern='^(NOIAMNOT|YESIAM)$')
