from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    password = forms.CharField(label="Password", max_length=100, widget=forms.PasswordInput(attrs={'class': 'sul-text-field'}))


class UserSettingsForm(forms.Form):
    old_password = forms.CharField(label="Old Password", max_length=100,
                               widget=forms.PasswordInput(attrs={'class': 'sul-text-field'}))
    password = forms.CharField(label="Password", max_length=100, widget=forms.PasswordInput(attrs={'class': 'sul-text-field'}))
    password_repeat = forms.CharField(label="Repeat Password", max_length=100,
                               widget=forms.PasswordInput(attrs={'class': 'sul-text-field'}))