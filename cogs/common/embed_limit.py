FIELD_COUNT = 25
NAME = 256
FIELD_VALUE = 1024
TOTAL = 6000

def over(embed):
    return len(embed) > TOTAL or len(embed.fields) > FIELD_VALUE