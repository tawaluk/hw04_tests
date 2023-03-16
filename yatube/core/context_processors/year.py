import datetime


def year(request):
    return {
        'year': int(datetime.datetime.today().strftime('%Y')),
    }
