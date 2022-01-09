import random
import string
import os

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your models here.
from django.utils.text import slugify
from emoji_picker.widgets import EmojiPickerTextInputAdmin


def user_files(instance, filename):
    return '/'.join(['telegram_users', str(instance.id), filename])


def photo_encodings(instance, filename):
    return '/'.join(['events', str(instance.event.id), 'photos', str(instance.id), filename])


def default_category():
    return Category.objects.get_or_create(name='default')[0]


def validate_spaces(value):
    if ' ' in value:
        raise ValidationError(
            '%(value)s contiene degli spazi. Non sono ammessi',
            params={'value': value},
        )


def event_code():
    length = 6

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Event.objects.filter(code=code).count() == 0:
            break

    return code


def auth_token():
    length = 16

    while True:
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        if Authentication.objects.filter(token=token).count() == 0:
            break

    return token


def get_unique_slug(model, field_name, value):
    max_length = model._meta.get_field(field_name).max_length
    slug = slugify(value)
    num = 1
    unique_slug = slug[:max_length - len(str(num)) - 1]
    if not model.objects.filter(**{field_name: unique_slug}).exists():
        return unique_slug
    unique_slug = '{}-{}'.format(slug[:max_length - len(str(num)) - 1], num)
    while model.objects.filter(** {field_name: unique_slug}).exists():
        unique_slug = '{}-{}'.format(slug[:max_length - len(str(num)) - 1], num)
        num += 1
    return unique_slug


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Category(models.Model):
    name = models.CharField(
        "Name",
        max_length=50,
        help_text="Nome della categoria",
        unique=True
    )
    description = models.TextField(
        "Description",
        help_text="Descrizione della categoria",
        blank=True,
        null=True
    )
    emoji = models.CharField(
        "Emoji",
        max_length=10,
        help_text="Emoji della categoria",
        default="🐴"
    )
    status = models.BooleanField(
        "Stato",
        help_text="Se attivo, la categoria può essere utilizzata per definire un evento",
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return f"{self.name} {self.emoji}"

    @classmethod
    def my_name(cls_):
        return cls_.__name__


class Address(models.Model):
    raw = models.CharField(
        "Completo",
        max_length=200,
        help_text="<strong>Obbligatorio.</strong><br><br>"
                  "Indirizzo composto da tutti i campi.<br>Se questo metodo viene utilizzato, si perdono "
                  "informazioni utili"
    )
    street = models.CharField(
        "Via/Viale/Piazza",
        max_length=50,
        help_text="Via, viale, strada o piazza dell\'indirizzo",
        blank=True,
        null=True
    )
    street_number = models.CharField(
        "Numero civico",
        max_length=10,
        help_text="Numero civico dell\'indirizzo.<br>Può contenere anche lettere e simboli",
        blank=True,
        null=True
    )
    city = models.CharField(
        "Città",
        max_length=50,
        blank=True,
        null=True
    )
    postal_code = models.CharField(
        "CAP",
        max_length=10,
        help_text="Codice di avviamento postale",
        blank=True,
        null=True
    )
    region = models.CharField(
        "Regione",
        max_length=50,
        blank=True,
        null=True
    )
    state = models.CharField(
        "Stato",
        max_length=50,
        blank=True,
        null=True
    )
    status = models.BooleanField(
        "Stato",
        help_text="Se attivo, l\'indirizzo può essere utilizzato per definire un evento",
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'address'
        verbose_name = 'address'
        verbose_name_plural = 'addresses'

    def __str__(self):
        return f"{self.raw}"

    @classmethod
    def my_name(cls_):
        return cls_.__name__


class TelegramUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    username = models.CharField(
        "Username",
        max_length=50,
        null=True,
        blank=True
    )
    first_name = models.CharField(
        "Nome",
        max_length=50,
        default=None,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        "Cognome",
        max_length=50,
        default=None,
        blank=True,
        null=True
    )
    url_encodings = models.FileField(
        "Encodings",
        upload_to=user_files,
        default=None,
        blank=True,
        null=True,
        storage=OverwriteStorage()
    )
    url_video = models.FileField(
        "Video",
        upload_to=user_files,
        default=None,
        blank=True,
        null=True,
        storage=OverwriteStorage()
    )
    status = models.BooleanField("Stato", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telegram_user'
        verbose_name = 'telegram_user'
        verbose_name_plural = 'telegram_users'

    @staticmethod
    def generate_constructor(user):
        all_fields = [f.name for f in TelegramUser._meta.fields]
        new_user = dict()
        for key, value in user.items():
            if key in all_fields:
                new_user[key] = value
        return new_user

    @classmethod
    def my_name(cls_):
        return cls_.__name__

    def __str__(self):
        return self.username


class Authentication(models.Model):
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE
    )
    token = models.CharField(
        "Token",
        max_length=16,
        default=auth_token
    )
    expiration = models.DateTimeField()
    is_login = models.BooleanField(default=True)

    class Meta:
        db_table = 'authentication'
        verbose_name = 'authentication'
        verbose_name_plural = 'authentications'

    @classmethod
    def my_name(cls_):
        return cls_.__name__

    def __str__(self):
        return self.token


class Photographer(models.Model):
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='photographer'
    )
    name = models.CharField(
        "Name",
        max_length=50,
        help_text="Nome da fotografo"
    )
    website = models.URLField(
        "Sito web",
        help_text="Url del sito web del fotografo",
        blank=True,
        null=True
    )
    instagram = models.URLField(
        "Instagram",
        help_text="Username del profilo instagram",
        blank=True,
        null=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        editable=False
    )
    disk_space = models.PositiveIntegerField(
        "Spazio su disco",
        help_text="Lo spazio, in MB, su disco dedicato all\'upload di file zip quando ad esempio "
                  "non si possiede un sito web dove caricare gli album",
        default=500
    )
    status = models.BooleanField(
        "Stato",
        help_text="Se attivo, tutti gli eventi di questo fotografo sono visibili",
        default=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photographer'
        verbose_name = 'photographer'
        verbose_name_plural = 'photographers'

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def my_name(cls_):
        return cls_.__name__

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self.__class__, 'slug', self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET(default_category),
        related_name='events'
    )
    photographer = models.ForeignKey(
        Photographer,
        on_delete=models.CASCADE,
        related_name='events'
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True
    )
    name = models.CharField(
        "Name",
        max_length=50,
        help_text="Nome dell\'evento"
    )
    description = models.TextField(
        "Descrizione",
        help_text="Informazioni aggiuntive sull\'evento",
        null=True,
        blank=True
    )
    url = models.CharField(
        "Url album",
        max_length=200,
        help_text="Url dell\'album dove sono contenute le foto dell\'evento.<br>"
                  "Può essere anche il percorso al file zip con le foto"
    )
    date = models.DateField(
        "Data evento"
    )
    code = models.CharField(
        "Codice",
        max_length=6,
        help_text="Codice univoco dell\'evento. Serve a trovare in modo puntuale l\'evento.",
        default=event_code
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        editable=False
    )
    is_public = models.BooleanField(
        "Pubblico",
        help_text="Se attivo, l\'evento è indicizzato e può comparire nelle liste di ricerca.<br>"
                  "Se disattivo, l\'evento è da considerarsi privato è può essere visto solo da "
                  "chi possiede il codice univoco"
    )
    status = models.BooleanField(
        "Stato",
        help_text="Se attivo, questo evento è indicizzato.<br>"
                  "Questa regola sovrasta anche la regola pubblico/privato",
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event'
        verbose_name = 'event'
        verbose_name_plural = 'events'

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def my_name(cls_):
        return cls_.__name__

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self.__class__, 'slug', self.name)
        super().save(*args, **kwargs)


class Photo(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    url = models.CharField(
        "Url foto",
        max_length=200,
        help_text="Url della foto. Può essere anche un percorso"
    )
    faces = models.FileField(
        "Encodings",
        upload_to=photo_encodings,
        default=None,
        blank=True,
        null=True
    )
    status = models.BooleanField(
        "Stato",
        help_text="Se attivo, la foto viene utilizzata nella ricerca",
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photo'
        verbose_name = 'photo'
        verbose_name_plural = 'photos'

    def __str__(self):
        return f"{self.url}"

    @classmethod
    def my_name(cls_):
        return cls_.__name__


class PhotoMatch(models.Model):
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    accuracy = models.FloatField(
        "Accuratezza",
        help_text="Valore in percentuale sull\'accuratezza del match"
    )
    status = models.BooleanField(
        "Stato",
        help_text="Se attivo, il match viene mostrato all'utente che lo richiede",
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photomatch'
        verbose_name = 'photomatch'
        verbose_name_plural = 'photomatches'

    def __str__(self):
        return f"Match for user {self.telegram_user} and photo {self.photo}"

    @classmethod
    def my_name(cls_):
        return cls_.__name__


class BotMessage(models.Model):
    name = models.CharField(
        "Nome",
        max_length=50,
        help_text="Questo è il nome del messaggio che verrà utilizzato nel codice per "
                  "identificare il corpo del messaggio stesso.<br><strong>Non ci possono essere "
                  "spazi fra le parole.</strong><br>Una volta creato non potrà essere modificato.",
        unique=True,
        validators=[validate_spaces]
    )
    body = models.TextField(
        "Corpo",
        help_text="Questo è il corpo del messaggio che viene effettivamente mostrato "
                  "all\'utente.<br>Utilizza le <strong>{}</strong> con una parola all\'interno "
                  "per sostituire quella porzione del testo stesso con un\'informazione personale "
                  "dell\'utente.<br>Ad esempio usa {nome} per inserire il nome dell\'utente."
    )
    description = models.TextField(
        "Descrizione",
        help_text="Aggiungi una descrizione dettagliata o meno sul messaggio.<br>Ad esempio "
                  "se il messaggio deve comparire alla pressione di un pulsante.<br>Il campo "
                  "non è richiesto quindi può essere lasciato vuoto",
        blank=True,
        null=True
    )
    status = models.BooleanField(
        "Stato",
        help_text="Usa questo campo per definire se il messaggio deve essere preso in "
                  "considerazione nel codice.<br>Puoi scegliere di disattivarlo per poi usarlo "
                  "in futuro.",
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bot_message'
        verbose_name = 'bot_message'
        verbose_name_plural = 'bot_messages'

    @classmethod
    def my_name(cls_):
        return cls_.__name__

    def __str__(self):
        return self.name
