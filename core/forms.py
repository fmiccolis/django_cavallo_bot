from django import forms
from emoji_picker.widgets import EmojiPickerTextInputAdmin, EmojiPickerTextareaAdmin

from core.models import Category


class CategoryForm(forms.ModelForm):
    emoji = forms.CharField(widget=EmojiPickerTextInputAdmin)

    class Meta:
        model = Category
        fields = '__all__'
