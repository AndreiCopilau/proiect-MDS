from django.contrib.auth.forms import UserCreationForm
from .models import UserCustom
from django.core.exceptions import ValidationError
from django import forms
from django.core.exceptions import ValidationError
from datetime import date


class UserCustomForm(UserCreationForm):
    class Meta:
        model = UserCustom
        fields = [
            'username', 'email', 'telefon',
            'data_nasterii', 'gen', 'password1', 'password2'
        ]
        labels = {
            'username': 'Utilizator',
            'email': 'Email',
            'telefon': 'Telefon',
            'data_nasterii': 'Data nasterii',
            'gen': 'Gen',
            'password1': 'Parola',
            'password2': 'Confirma parola',
        }
        help_texts = {
            'username': 'Introduceti un nume unic pentru utilizator.',
            'password1': 'Parola trebuie sa fie puternica.',
        }
        widgets = {
            'data_nasterii': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if not telefon.isdigit():
            raise ValidationError("Numarul de telefon trebuie sa contina doar cifre.")
        if not (10 <= len(telefon) <= 15):
            raise ValidationError("Numarul de telefon trebuie sa aiba intre 10 si 15 caractere.")
        return telefon

    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data.get('data_nasterii')
        if data_nasterii:
            today = date.today()
            varsta = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
            if varsta < 14:
                raise ValidationError("Trebuie sa aveti cel putin 14 ani pentru a va inregistra.")
        return data_nasterii

from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    ramane_logat = forms.BooleanField(
        required=False,
        initial=False,
        label="Ramaneti logat"
    )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data