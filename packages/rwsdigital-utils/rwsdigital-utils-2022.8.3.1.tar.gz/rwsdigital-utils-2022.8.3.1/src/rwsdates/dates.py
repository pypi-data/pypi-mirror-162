from datetime import datetime
from datetime import timedelta

# input: stringa contenente una data in qualsiasi formato
# output: oggetto datetime.datetime con la data corrispondente
def str_to_datetime(date_string):
    most_used_formats = ["%Y/%m/%d %H.%M.%S",
                         "%Y/%m/%d %H:%M:%S",
                         "%Y-%m-%d %H.%M.%S",
                         "%Y-%m-%d %H:%M:%S",
                         "%d/%m/%Y %H.%M.%S",
                         "%d/%m/%Y %H:%M:%S",
                         "%d-%m-%Y %H.%M.%S",
                         "%d-%m-%Y %H:%M:%S",
                         "%Y/%m/%d %H.%M",
                         "%Y/%m/%d %H:%M",
                         "%Y-%m-%d %H.%M",
                         "%Y-%m-%d %H:%M",
                         "%d/%m/%Y %H.%M",
                         "%d/%m/%Y %H:%M",
                         "%d-%m-%Y %H.%M",
                         "%d-%m-%Y %H:%M",
                         "%Y/%m/%d",
                         "%Y-%m-%d",
                         "%d/%m/%Y",
                         "%d-%m-%Y"]
    for format_ in most_used_formats:
        try:
            res = datetime.strptime(date_string, format_)
            return res
        except ValueError:
            continue
    raise ValueError("Formato data non supportato ({})".format(date_string))

# input: stringa contenente una data in qualsiasi formato
# output: oggetto datetime.date con la data corrispondente
def str_to_date(date_string):
    return str_to_datetime(date_string).date()

# input: stringa contenente il numero del mese richiesto
# output: datetime.datetime con l'ultimo giorno del mese della data in ingresso
def last_day_of_month(month):
    if len(month) == 1:
        month = '0' + month
    year = str(datetime.now().year)
    str_date = '01/' + month + '/' + year
    tmp_date = str_to_date(str_date)
    next_month = tmp_date.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)
