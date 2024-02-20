from django import forms
class CrawlerForm(forms.Form):
    session_id = forms.CharField(label="session_id", max_length=10, widget=forms.HiddenInput())
    dead_included = forms.BooleanField(label="dead_included", widget=forms.CheckboxInput())