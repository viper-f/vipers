from django import forms


class UrlForm(forms.Form):
    url = forms.CharField(label="Url", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    start_url = forms.CharField(label="Start Url", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    template = forms.CharField(label="template", widget=forms.Textarea(attrs={"rows": "5", 'class': 'sul-text-field'}))
    custom_credentials = forms.BooleanField(label="Custom Credentials", widget=forms.CheckboxInput(attrs={'class': 'sul-checkbox-type-2'}))
    custom_username = forms.CharField(label="Custom Username", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    custom_password = forms.CharField(label="Custom Password", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))