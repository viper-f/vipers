from django import forms

from advertiser.models import AdTemplate


class AdForm(forms.Form):
    session_id = forms.CharField(label="sessionid", max_length=10, widget=forms.HiddenInput())
    url = forms.CharField(label="Url", max_length=100, widget=forms.HiddenInput())
    templates = forms.ChoiceField(label="Chosen Templates",
                                         widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked', 'class': ''}),
                                         required=False)
    custom_credentials = forms.BooleanField(label="Custom Credentials",
                                            widget=forms.CheckboxInput(attrs={'class': 'sul-checkbox-type-2'}), required=False)
    custom_username = forms.CharField(label="Custom Username", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'sul-text-field'}), required=False)
    custom_password = forms.CharField(label="Custom Password", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'sul-text-field'}), required=False)

    def __init__(self, *args, **kwargs):
        self.forum_id = kwargs.pop("forum_id")
        super(AdForm, self).__init__(*args, **kwargs)
        self.fields['templates'].choices = self.get_templates()

    def get_templates(self):
        templates = AdTemplate.objects.filter(home_forum=self.forum_id)
        choices = []
        for template in templates:
            choices.append((template.id, template.name))
        return choices



class PartnerForm(forms.Form):
    session_id = forms.CharField(label="sessionid", max_length=10, widget=forms.HiddenInput())
    urls = forms.CharField(label="Urls", widget=forms.Textarea(attrs={"rows": "10", 'class': 'sul-text-field'}))
    template = forms.CharField(label="Template", widget=forms.Textarea(attrs={"rows": "5", 'class': 'sul-text-field'}))


class ForumForm(forms.Form):
    id = forms.CharField(label="id", max_length=10, widget=forms.HiddenInput())
    name = forms.CharField(label="Name", max_length=100, widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    ad_topic_url = forms.CharField(label="Current Ad Topic", max_length=100,
                               widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    partner_urls = forms.CharField(label="Urls of Partner Topics",
                                   widget=forms.Textarea(attrs={"rows": "10", 'class': 'sul-text-field'}), required=False)
    custom_credentials = forms.BooleanField(label="Custom Credentials",
                                            widget=forms.CheckboxInput(attrs={'class': 'sul-checkbox-type-2'}), required=False)
    custom_username = forms.CharField(label="Custom Username", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'sul-text-field'}), required=False)
    custom_password = forms.CharField(label="Custom Password", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'sul-text-field'}), required=False)


class AdTemplateForm(forms.Form):
    forum_id = forms.CharField(label="forum_id", max_length=10, widget=forms.HiddenInput())
    name = forms.CharField(label="Name", widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    code = forms.CharField(label="Code", widget=forms.Textarea(attrs={"rows": "5", 'class': 'sul-text-field'}))
    priority = forms.CharField(label="priority", widget=forms.HiddenInput())
