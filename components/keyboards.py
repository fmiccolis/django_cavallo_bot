import emoji
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_navigation = [
    InlineKeyboardButton(text=f"{emoji.emojize(':last_track_button:', use_aliases=True)}", callback_data="FIRST_ELEMENT"),
    InlineKeyboardButton(text=f"{emoji.emojize(':arrow_backward:', use_aliases=True)}", callback_data="PREV_ELEMENT"),
    InlineKeyboardButton(text=f"{emoji.emojize(':arrow_forward:', use_aliases=True)}", callback_data="NEXT_ELEMENT"),
    InlineKeyboardButton(text=f"{emoji.emojize(':next_track_button:', use_aliases=True)}", callback_data="LAST_ELEMENT")
]

current_element_button = InlineKeyboardButton(text="{0}/{1}", callback_data="CURRENT_ELEMENT")

keyboard_scan_edit = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Messaggio token", callback_data="TOKEN_MESSAGE"),
    InlineKeyboardButton(text="Modifica le informazioni", callback_data="EDIT_EVENT")
], [
    InlineKeyboardButton(text="Attiva/Disattiva", callback_data="TOGGLE_EVENT"),
    InlineKeyboardButton(text="Rimuovi evento", callback_data="REMOVE_EVENT")
], [
    InlineKeyboardButton(text="Ricomincia lo scanning del sito", callback_data="RESTART_SCAN")
]])

keyboard_edit_grapher = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Elimina il mio account fotografo", callback_data="REMOVE_GRAPHER"),
    InlineKeyboardButton(text="Modifica le informazioni", callback_data="EDIT_GRAPHER")
]])

keyboardconfirm = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Abilita/Disabilita!", callback_data="TOGGLE_PHOTOGRAPHER"),
    InlineKeyboardButton(text="Scopri gli eventi!", callback_data="SHOW_EVENT"),
    InlineKeyboardButton(text="Elimina il mio account fotografo", callback_data="REMOVE_GRAPHER")
]])

keyboard_show_event = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Scopri gli eventi!", callback_data="SHOW_EVENT")
]])

keyboard_toggle_edit_category = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Abilita/Disabilita", callback_data="TOGGLE_CATEGORY"),
    InlineKeyboardButton(text="Modifica i dati", callback_data="EDIT_CATEGORY")
]])

keyboard_remove_edit_category = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Abilita/Disabilita", callback_data="TOGGLE_CATEGORY"),
    InlineKeyboardButton(text="Modifica i dati", callback_data="EDIT_CATEGORY"),
    InlineKeyboardButton(text="Rimuovi", callback_data="REMOVE_CATEGORY")
]])

keyboard_toggle_edit_video_data = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Rimuovi il video", callback_data="REMOVE_VIDEO")
], [
    InlineKeyboardButton(text="Cambia il video", callback_data="EDIT_VIDEO")
]])

keyboard_find_face = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Messaggio token", callback_data="TOKEN_MESSAGE"),
    InlineKeyboardButton(text="Cerca il mio volto!", callback_data="FIND_FACE")
]])

keyboard_is_me = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="Aspetta, ma non sono io!", callback_data="NOIAMNOT"),
    InlineKeyboardButton(text="Si, sono proprio io!", callback_data="YESIAM")
]])

test_keyboard = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="bottone test1", callback_data="TEST1"),
    InlineKeyboardButton(text="bottone test2", callback_data="TEST2")
]])

navigation = {
    'events': {
        'owner': keyboard_scan_edit,
        'viewer': keyboard_find_face
    },
    'photographers': {
        'devs': keyboardconfirm,
        'owner': keyboard_edit_grapher,
        'viewer': keyboard_show_event
    },
    'categories': {
        'devs': keyboard_remove_edit_category,
        'viewer': keyboard_show_event
    }
}
