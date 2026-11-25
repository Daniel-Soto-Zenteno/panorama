from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Actividad, Comunidad, Lugar, Perfil


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Correo privado')
    consentimiento = forms.BooleanField(label='Acepto el uso de mi cuenta para este prototipo académico y he leído el aviso de privacidad.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'username': 'Nombre de usuario público'}

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre', 'descripcion', 'intereses']


class ComunidadForm(forms.ModelForm):
    class Meta:
        model = Comunidad
        fields = ['nombre', 'descripcion']


class LugarForm(forms.ModelForm):
    class Meta:
        model = Lugar
        fields = ['nombre', 'descripcion', 'zona', 'latitud', 'longitud']


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['titulo', 'descripcion', 'categoria', 'comunidad', 'lugar', 'todo_el_ano', 'horario', 'hora_inicio', 'hora_fin', 'fecha_hora', 'fin']
        widgets = {**{f: forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M') for f in ['fecha_hora', 'fin']}, **{f: forms.TimeInput(attrs={'type': 'time'}) for f in ['hora_inicio', 'hora_fin']}}
        labels = {'fecha_hora': 'Inicio (hora de Chile)', 'fin': 'Fin (hora de Chile)', 'todo_el_ano': 'Disponible todo el año', 'horario': 'Horario habitual (solo todo el año)'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comunidad'].queryset = Comunidad.objects.filter(estado='APROBADO')
        self.fields['lugar'].queryset = Lugar.objects.filter(estado='APROBADO')
        self.fields['comunidad'].required = self.fields['lugar'].required = True
        self.fields['descripcion'].required = True


class TextoForm(forms.Form):
    texto = forms.CharField(max_length=3000, widget=forms.Textarea(attrs={'rows': 3}), label='Tu mensaje')


class MotivoForm(forms.Form):
    motivo = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 2}), label='Motivo de la acción')
