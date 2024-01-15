from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def index(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('vipers:index'))


