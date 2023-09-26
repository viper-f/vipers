from django import forms


class UrlForm(forms.Form):
    url = forms.CharField(label="Url", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))