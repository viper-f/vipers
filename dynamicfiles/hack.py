from http.cookies import Morsel


class MyMorsel(Morsel):
    _reserved = {
        "expires"  : "expires",
        "path"     : "Path",
        "comment"  : "Comment",
        "domain"   : "Domain",
        "max-age"  : "Max-Age",
        "secure"   : "Secure",
        "httponly" : "HttpOnly",
        "version"  : "Version",
        "samesite" : "SameSite",
        "partitioned": "Partitioned"
    }

    _flags = {'secure', 'httponly', 'partitioned'}