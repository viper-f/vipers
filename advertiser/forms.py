from django import forms


class AdForm(forms.Form):
    session_id = forms.CharField(label="sessionid", max_length=10, widget=forms.HiddenInput())
    url = forms.CharField(label="Url", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    start_url = forms.CharField(label="Start Url", max_length=100,
                                widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    template = forms.CharField(label="Template", widget=forms.Textarea(attrs={"rows": "5", 'class': 'sul-text-field'}))
    custom_credentials = forms.BooleanField(label="Custom Credentials",
                                            widget=forms.CheckboxInput(attrs={'class': 'sul-checkbox-type-2'}))
    custom_username = forms.CharField(label="Custom Username", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    custom_password = forms.CharField(label="Custom Password", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'sul-text-field'}))


class PartnerForm(forms.Form):
    session_id = forms.CharField(label="sessionid", max_length=10, widget=forms.HiddenInput())
    urls = forms.CharField(label="Urls",  widget=forms.Textarea(attrs={"rows": "10", 'class': 'sul-text-field'}))
    template = forms.CharField(label="Template", widget=forms.Textarea(attrs={"rows": "5", 'class': 'sul-text-field'}))
