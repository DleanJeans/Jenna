import base64

LSTV_URL = 'https://tuvilyso.vn/lasotuvi/%s.png'
LSTV_SETTINGS = '1|5|0|1|1|0|0|%s|00|1|7|2'
DEFAULT_NAME = 'Psychic Ritord'

def compile_url(dob, birthtime, gender, name):
    name = name or DEFAULT_NAME

    day, month, year = dob.numbers
    horoscope_hour = compute_horoscope_hour(birthtime)

    data = [year, month, day, horoscope_hour, gender, name, LSTV_SETTINGS % birthtime]
    data = '|'.join(str(d) for d in data)
    data = base64.b64encode(bytes(data, 'utf-8')).decode('ascii')

    image_url = LSTV_URL % data
    return image_url

def compute_horoscope_hour(hour):
    hh = (hour + 1) // 2 + 1
    if hh == 13:
        hh = 1
    return hh