import os
import pickle
import time
import urllib.request
from datetime import datetime

import cv2
import face_recognition
import validators
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, CommandHandler, \
    CallbackContext

from botConfig import get_time_left, horserace, cancel, CONV_TIMEOUT
from core.models import TelegramUser, Photo, PhotoMatch, Event
from components import keyboards
from botLogger import logger as pm_logger

SENDSEARCH = range(1)
extra = {'file_name': 'FindFace.py'}


def find_face(update: Update, context: CallbackContext):
    pm_logger.info(extra=extra, msg=f"Request find_face")
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    evento: Event = context.user_data['evento']
    tg_user: TelegramUser = TelegramUser.objects.get(id=user_id)
    context.user_data['tg_user'] = tg_user
    photos = Photo.objects.filter(matches__telegram_user=tg_user, matches__status=True, event=evento)
    if len(photos) > 0:
        pm_logger.info(extra=extra, msg=f"Request find_face. match founded for event {evento.id}, total: {len(photos)}")
        keyboard_send_search = [['mandami le foto'], ['ricomanica la ricerca']]
        query.message.reply_text(
            "Per questo evento hai già cercato e trovato il tuo volto!\n"
            "Ti invio le foto oppure ricomincio la ricerca?",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard_send_search, one_time_keyboard=True)
        )
        context.user_data['photos_to_send'] = photos
        context.user_data['search_evento'] = evento
        return SENDSEARCH
    else:
        pm_logger.critical(extra=extra, msg=f"Request find_face. no match for event {evento}")
        query.message.reply_text(
            "Non ho trovato nessun salvataggio precedente con le foto con il tuo volto per questo evento.\n"
            "Faccio partire la ricerca!"
        )
        context.user_data['search_evento'] = evento
        return do_search(update, context)


def send_matches(update: Update, context: CallbackContext):
    pm_logger.info(extra=extra, msg=f"Request send_matches")
    message = update.message
    user_id = message.from_user.id
    photos = context.user_data['photos_to_send']
    message.reply_text(
        f"In totale ho trovato {len(photos)} con il tuo volto.\n"
        f"Adesso te le invio tutte", reply_markup=ReplyKeyboardRemove()
    )
    for photo in photos:
        context.bot.send_photo(chat_id=user_id, photo=photo.url)
    evento: Event = context.user_data['search_evento']
    message.reply_text("Ti invito a visitare la pagina del sito!\n\n" + evento.url)

    return ConversationHandler.END


def do_search(update: Update, context: CallbackContext):
    pm_logger.info(extra=extra, msg=f"Request do_search")
    telegram_user: TelegramUser = context.user_data['tg_user']
    message = update.effective_message
    if not telegram_user:
        pm_logger.critical(extra=extra, msg=f"Request do_search. no saved user")
        message.reply_text(
            "C'è stato un errore durante il salvataggio del tuo utente.\n"
            "Usa il comando /start per ricominciare la procedura"
        )
        return ConversationHandler.END

    encodings_url = telegram_user.url_encodings
    if not encodings_url:
        pm_logger.critical(extra=extra, msg=f"Request do_search. no saved encodings")
        message.reply_text(
            "Non hai ancora salvato il video e i dati del tuo volto.\n"
            "Senza di essi non posso effettuare la ricerca!\n"
            "Usa il comando /invia per salvare il video così potrò estrarre i dati!"
        )
        return ConversationHandler.END

    if not os.path.isfile(encodings_url.path):
        pm_logger.critical(extra=extra, msg=f"Request do_search. error while saving encodings")
        message.reply_text(
            "C\'è stato un errore nel salvataggio dei dati del tuo volto!\n"
            "Ti prego di riprovare a caricarli usando il comando /invia !"
        )
        return ConversationHandler.END
    known_encoding_path = encodings_url.path

    evento = context.user_data['search_evento']
    try:
        PhotoMatch.objects.filter(photo__event=evento, telegram_user=telegram_user).delete()
        photos = Photo.objects.filter(event=evento, status=True).exclude(faces='')
        if photos:
            pm_logger.info(extra=extra, msg=f"Request do_search. total photos: {len(photos)}")
            message.reply_text(
                f"Per questo evento ci sono {len(photos)} foto con dei volti!",
                reply_markup=ReplyKeyboardRemove()
            )
            with open(known_encoding_path, 'rb') as f:
                all_face_encodings: dict = pickle.load(f)

            base_keys = all_face_encodings.keys()
            known_encodings = list()
            for key in base_keys:
                if key == 'video':
                    for video_frame in all_face_encodings[key]:
                        known_encodings.append(video_frame['encoding'])
                else:
                    known_encodings.append(all_face_encodings[key]['encoding'])

            pm_logger.info(extra=extra, msg=f"Request do_search. generated encoding list, size: {len(known_encodings)}")

            known_faces = len(known_encodings)
            percent_message = message.reply_text(
                "Inizio con la ricerca del tuo volto"
            )
            total = len(photos)
            founded_photos = list()
            start_time = datetime.now()
            isdev = context.user_data.pop('is_dev_mode', False)
            temp_photo = f'temp{telegram_user.id}.jpg'
            runtime_dataset = dict()
            runtime_valid_encodings = list()
            for idx, photo in enumerate(photos):
                pm_logger.info(extra=extra, msg=f"analisi foto: {idx}")
                time.sleep(0.2 if isdev else 0.3)
                time_left = get_time_left(start_time, idx+1, total)
                percent = round((idx + 1) * 100 / total, 2)
                percent_message.edit_text(
                    text=f"{horserace(percent)}\ne ho trovato {len(founded_photos)} foto\n"
                         f"Tempo rimanente (stimato): {time_left}"
                )
                try:
                    with open(photo.faces.path, 'rb') as p_enc:
                        unknown_encodings = pickle.load(p_enc)

                    pm_logger.info(extra=extra, msg=f"aperto encoding")

                    for single_encoding in unknown_encodings:
                        result = face_recognition.compare_faces(known_encodings+runtime_valid_encodings, single_encoding['encoding'])
                        if sum(result) > (known_faces * 0.75):
                            accuracy = round((sum(result)/known_faces) * 100, 2)
                            if isdev:
                                urllib.request.urlretrieve(photo.url, temp_photo)
                                img = cv2.imread(temp_photo)
                                top, right, bottom, left = single_encoding['location']
                                cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 10)
                                cv2.imwrite(temp_photo, img)
                                context.bot.send_photo(
                                    chat_id=telegram_user.id,
                                    photo=open(temp_photo, 'rb'),
                                    caption=f"{accuracy} %\n{single_encoding['location']}"
                                )
                            if accuracy >= 90 and single_encoding['url'] not in base_keys:
                                pm_logger.info(extra=extra, msg=f"Request do_search. new valid encoding")
                                runtime_valid_encodings.append(single_encoding['encoding'])
                                runtime_dataset[single_encoding['url']] = {
                                    'location': single_encoding['location'],
                                    'encoding': single_encoding['encoding']
                                }
                                known_encodings.append(single_encoding['encoding'])
                                known_faces = len(known_encodings) + len(runtime_valid_encodings)
                            founded_photos.append({
                                "url": photo.url,
                                "id": photo,
                                "acc": accuracy,
                                "enc": single_encoding["encoding"],
                                "loc": single_encoding["location"]
                            })
                            break
                except ValueError as VE:
                    stringa = f"foto {(idx+1)} su {total}\nerrore: {VE}"
                    message.reply_text(stringa)
                except IndexError as IE:
                    stringa = f"foto {(idx+1)} su {total}\nerrore: {IE}"
                    message.reply_text(stringa)

            message.reply_text("Ho finito di analizzare, ora ti invio le foto")
            pm_logger.info(extra=extra, msg=f"Request do_search. search terminated")

            all_face_encodings.update(runtime_dataset)

            with open(known_encoding_path, 'wb') as f:
                pickle.dump(all_face_encodings, f)

            if os.path.exists(temp_photo):
                os.remove(temp_photo)

            pm_logger.info(extra=extra, msg=f"Request do_search. updated {known_encoding_path}")

            matches = dict()
            if len(founded_photos) > 0:
                pm_logger.info(extra=extra, msg=f"Request do_search. total valid photos: {len(founded_photos)}")
                for pho in founded_photos:
                    foto_msg = {
                        "chat_id": telegram_user.id,
                        "photo": pho["url"],
                        "reply_markup": keyboards.keyboard_is_me
                    }
                    if not validators.url(pho["url"]):
                        foto_msg["photo"] = open(pho["url"], 'rb')
                    photomessage = context.bot.send_photo(**foto_msg)
                    idmsg = photomessage.message_id
                    foto = pho["id"]
                    matchresult = PhotoMatch(telegram_user=telegram_user, photo=foto, accuracy=pho["acc"])
                    matchresult.save()
                    match_obj = {
                        "url": pho["url"],
                        "mid": matchresult
                    }
                    if pho["acc"] < 90:
                        match_obj.update({
                            "enc": pho["enc"],
                            "loc": pho["loc"],
                        })
                    matches[str(idmsg)] = match_obj

                context.user_data['matches_to_check'] = matches
                pm_logger.info(extra=extra, msg=f"Request do_search. saved matches")
            else:
                pm_logger.critical(extra=extra, msg=f"Request do_search. no matches")
                message.reply_text("Il tuo volto non è stato trovato in nessuna foto!")

            message.reply_text("Ti invito a visitare la pagina del sito!\n\n" + evento.url)
            return ConversationHandler.END
        else:
            pm_logger.critical(extra=extra, msg=f"Request do_search. no photos")
            message.reply_text(
                "Per questo evento non ci sono foto con dei volti quindi non posso cercare il tuo!"
            )
            return ConversationHandler.END
    except Exception as E:
        pm_logger.error(extra=extra, msg=f"Request do_search. error while deleting old mathces {E}")
        message.reply_text(
            "C'è stato un errore nel cancellare il salvataggio precendente per questo evento!"
        )
        return ConversationHandler.END


find_face_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(find_face, pattern='^(FIND_FACE)$')],

    states={
        SENDSEARCH: [
            MessageHandler(Filters.regex(r'mandami'), send_matches),
            MessageHandler(Filters.regex(r'ricomanica'), do_search)
        ]
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    conversation_timeout=CONV_TIMEOUT
)
