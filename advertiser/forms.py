from django import forms


class UrlForm(forms.Form):
    url = forms.CharField(label="Url", max_length=100)