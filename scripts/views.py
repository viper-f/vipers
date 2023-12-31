from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import escape

def index(request):
    return render(request, "scripts/index.html", {
                                                      "breadcrumbs": [
                                                          {"link": "/", "name": "Главная"},
                                                          {"link": "/scripts", "name": "Скрипты"}
                                                      ]
                                                      })

def post_calc(request):
    code = escape(render_to_string('scripts/post_calc_script.html'))
    return render(request, "scripts/post_calc.html", {
                                                      "code": code,
                                                      "breadcrumbs": [
                                                          {"link": "/", "name": "Главная"},
                                                          {"link": "/scripts", "name": "Скрипты"},
                                                          {"link": "/scripts/post_calc", "name": "Подсчет постов для банка"}
                                                      ]
                                                      })