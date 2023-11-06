import requests


def get_category(count):
    if count < 5000:
        return {
            "category": 1,
            "currency": 1
        }
    if count < 10000:
        return {
            "category": 2,
            "currency": 2
        }
    if count < 15000:
        return {
            "category": 3,
            "currency": 3
        }
    return {
        "category": 4,
        "currency": 4
    }


def get_category_text(category):
    return str(category) + ' билета'
