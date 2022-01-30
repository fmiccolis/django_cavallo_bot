import mimetypes
import os
import pathlib
import pickle
import threading
import urllib.request
from datetime import datetime
from zipfile import ZipFile

import face_recognition
import cv2 as cv
import requests
import validators
from PIL import UnidentifiedImageError
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from telegram import Update, Message
from telegram.ext import ConversationHandler, CallbackContext

from botConfig import EVENT_ENCODINGS_PATH, EVENT_PHOTOS_PATH, get_time_left, INSTAGRAM_BASE_URL
from core.models import Photo, Event


def get_encodings_from_video(video_url) -> dict:
    tg_user_id = video_url.split(os.sep)[-2]
    input_movie = cv.VideoCapture(video_url)

    # Initialize some variables
    user_face_encodings = list()
    length = int(input_movie.get(cv.CAP_PROP_FRAME_COUNT))
    fps = float(input_movie.get(cv.CAP_PROP_FPS))
    mcm = int(length / fps)
    frame_number = 0
    while input_movie.isOpened():
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 1

        # Quit when the input video file ends
        if not ret:
            break

        if frame_number % mcm != 0:
            continue

        try:
            # Find all the faces and face encodings in the current frame of video
            cv.imwrite(f'temp{tg_user_id}.jpg', frame)
            img = face_recognition.load_image_file(f'temp{tg_user_id}.jpg')
            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)
            if face_encodings:
                frame_info = {
                    'location': face_locations[0],
                    'encoding': face_encodings[0]
                }
                user_face_encodings.append(frame_info)
                print(f"Writing frame {frame_number} / {length}")
        except Exception as E:
            print(f"Errore {E}")

    # All done!
    os.remove(f'temp{tg_user_id}.jpg')
    input_movie.release()
    cv.destroyAllWindows()
    return {'video': user_face_encodings}


def start_scanning(update: Update, context: CallbackContext):
    message_object = update.effective_message
    msg = message_object.reply_text("Perfetto inizio a scannerizzare il sito!")
    evento: Event = context.user_data["evento"]
    Photo.objects.filter(event=evento).delete()
    url = evento.url
    internal = False
    if validators.url(url):
        real_img_list = extract_from_external_url(url, msg)
    else:
        internal = True
        real_img_list = extract_from_internal_url(url, evento.id)

    evento.is_scanning = True
    evento.save()
    scanning_thread = threading.Thread(target=do_scan, args=(message_object, real_img_list, evento, internal, msg,))
    scanning_thread.start()
    return ConversationHandler.END


def do_scan(message_object: Message, real_img_list: list, evento: Event, internal: bool, msg: Message):
    progress_msg = message_object.reply_text(f"Sto analizzando la foto 0 / {len(real_img_list)}.\n0.00 %")
    real_saved = 0
    start_time = datetime.now()
    total = len(real_img_list)
    temp_photo = f'temp{evento.id}.jpg'
    for idx, photo in enumerate(real_img_list):
        time_left = get_time_left(start_time, idx + 1, total)
        percentage = round((idx + 1) / len(real_img_list) * 100, 2)
        progress_msg.edit_text(
            f"Sto analizzando la foto {(idx + 1)} / {len(real_img_list)}.\n{percentage} %\n\n"
            f"Tempo rimanente (stimato): {time_left}"
        )
        foto_dict = {
            'url': photo,
            'event': evento
        }
        try:
            db_photo = Photo(**foto_dict)
            db_photo.save()
            try:
                if internal:
                    unknown_image = face_recognition.load_image_file(db_photo.url)
                else:
                    urllib.request.urlretrieve(db_photo.url, temp_photo)
                    unknown_image = face_recognition.load_image_file(temp_photo)
                face_locations = face_recognition.face_locations(unknown_image)
                face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
                if face_encodings:
                    this_photo_data = list()
                    for pos, encoding in enumerate(face_encodings):
                        this_face_data = {
                            'location': face_locations[pos],
                            'encoding': encoding,
                            'url': db_photo.url
                        }
                        this_photo_data.append(this_face_data)
                    db_photo.faces.save(f'{db_photo.id}encodings.dat', ContentFile(pickle.dumps(this_photo_data)))
                    db_photo.save()
                    real_saved += 1
                    print("salvata la foto e i dati di {0}".format(db_photo.url))
            except UnidentifiedImageError as UIE:
                print(f"errore durante analisi di {db_photo.url} con errore {UIE}")
        except Exception as E:
            print(f"Errore {E}")

    if os.path.exists(temp_photo):
        os.remove(temp_photo)

    msg.edit_text(f"Ho salvato {real_saved} foto.")


def extract_from_external_url(url: str, message: Message) -> list:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    image_list = dict()
    images = soup.find_all('img', attrs={"srcset": True, "src": True})
    message.edit_text(f"All\'indirizzo {url} ho trovato {len(images)} foto.\nAdesso le analizzo")
    for img in images:
        realimg = img['srcset'].split(",")[-1].strip().split(" ")[0]
        if realimg is None or realimg == "":
            realimg = img['src']
        validate_and_update(realimg, image_list)

    images = soup.find_all('a')
    for img in images:
        realimg = img['href']
        validate_and_update(realimg, image_list)

    real_img_list = [image_list[key] for key in image_list]
    message.edit_text(f"Delle foto trovate {len(real_img_list)} sono valide.")
    return real_img_list


def extract_from_internal_url(url: str, evento_id: int) -> list:
    event_photos_path = EVENT_PHOTOS_PATH.format(evento_id)
    print(pathlib.Path(__file__).parent.absolute())
    print(pathlib.Path().absolute())
    path = os.path.join(pathlib.Path().absolute(), url)
    if os.path.exists(path):
        print("esiste")
        with ZipFile(path, 'r') as p_zip:
            p_zip.extractall(event_photos_path)
            namelist = p_zip.namelist()
        return [os.path.join(event_photos_path, single_photo) for single_photo in namelist]
    return list()


def validate_and_update(real_img, imglist):
    root, ext = os.path.splitext(real_img)
    final_name = root.split("/")[-1].split("-")[0] + ext
    first, second = mimetypes.guess_type(final_name)
    if first:
        # print(final_name)
        if not imglist.get(final_name, None) and final_name != "":
            imglist[final_name] = real_img


def download_and_extract_zip(update: Update, context: CallbackContext):
    file_zip = update.message.document
    real_file = file_zip.get_file(timeout=200)
    context.user_data['url'] = real_file


def validate_ig_username(username: str = None) -> bool:
    if not username:
        return False
    url_profile = INSTAGRAM_BASE_URL.format(username)
    response = requests.get(url_profile)
    if response.status_code == 404:
        return False
    return True
