from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from classes.models import ClassSection


tw = 'w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition'


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': tw,
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': tw,
        'placeholder': 'Password',
    }))


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'assigned_class']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = tw
        self.fields['assigned_class'].queryset = ClassSection.objects.select_related('department').all()
        self.fields['assigned_class'].required = False


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'assigned_class']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = tw
        self.fields['assigned_class'].queryset = ClassSection.objects.select_related('department').all()
        self.fields['assigned_class'].required = False
