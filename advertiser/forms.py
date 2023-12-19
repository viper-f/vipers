from django import forms
from django.contrib.auth.models import User
from django_select2 import forms as s2forms
from advertiser.models import AdTemplate, CustomCredentials, HomeForum, Forum


class AdForm(forms.Form):
    session_id = forms.CharField(label="sessionid", max_length=10, widget=forms.HiddenInput())
    url = forms.CharField(label="Url", max_length=100, widget=forms.HiddenInput())
    templates = forms.ChoiceField(label="Priority Template",
                                         widget=forms.RadioSelect(attrs={'class': 'temp-radio'}))
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
        templates = AdTemplate.objects.filter(home_forum=self.forum_id).order_by("priority")
        choices = [(0, 'Default')]
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


class ScheduleItemForm(forms.Form):
    forum_id = forms.CharField(label="forum_id", max_length=10, widget=forms.HiddenInput())
    week_day = forms.MultipleChoiceField(label="Week day", widget=forms.CheckboxSelectMultiple())
    time_start = forms.TimeField(label="Start time", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'sul-text-field'}))
    custom_credentials = forms.ChoiceField(label="Custom Credentials", widget=forms.Select(attrs={'class': 'sul-select'}), required=False)

    def __init__(self, *args, **kwargs):
        self.forum_id = kwargs.pop("forum_id")
        self.user_id = kwargs.pop("user_id")
        super(ScheduleItemForm, self).__init__(*args, **kwargs)
        self.fields['custom_credentials'].choices = self.get_credentials()
        self.fields['week_day'].choices = [
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday')
    ]

    def get_credentials(self):
        credentials = CustomCredentials.objects.filter(home_forum=self.forum_id, user_id=self.user_id)
        choices = [(None, 'None')]
        for cred in credentials:
            choices.append((cred.id, cred.username))
        return choices



class HomeForumForm(forms.Form):
    name = forms.CharField(label="Name (label)", widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    ad_topic_url = forms.CharField(label="Ad Topic Url", widget=forms.TextInput(attrs={'class': 'sul-text-field'}))
    users = forms.MultipleChoiceField(label="Users",
                                         widget=forms.CheckboxSelectMultiple(attrs={'class': 'temp-radio'}))
    forum = forms.ChoiceField(label="Forum", widget=forms.Select(attrs={'class': 'sul-select'}))
    is_rusff =forms.BooleanField(label="Form Is Rusff", widget=forms.CheckboxInput(attrs={'class': 'sul-checkbox-type-2'}), required=False)

    def __init__(self, *args, **kwargs):
        super(HomeForumForm, self).__init__(*args, **kwargs)
        self.fields['users'].choices = self.get_users()
        self.fields['forum'].choices = self.get_forums()

    def get_users(self):
        users = User.objects.all()
        choices = []
        for user in users:
            choices.append((user.id, user.username))
        return choices

    def get_forums(self):
        forums = Forum.objects.filter(stop=False)
        choices = [(None, 'Select')]
        for forum in forums:
            choices.append((forum.id, forum.domain))
        return choices