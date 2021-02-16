REGION_OFFSET = 0x1f1a5
KEYCAP = '️⃣'
ALTERNATIVES = {
    'ABC': '🔤',
    'AB': '🆎',
    'COOL': '🆒',
    'FREE': '🆓',
    'ID': '🆔',
    'NEW': '🆕',
    'OK': '🆗',
    'OO': '➿',
    'SOS': '🆘',
    'UP': '🆙',
    'VS': '🆚',
    'WC': '🚾',
    'A': '🅰',
    'B': '🅱',
    'C': '☪',
    'H': '♓',
    'M': ['Ⓜ', '♍'],
    'N': '♑',
    'O': ['🅾', '⭕'],
    'P': '🅿',
    'T': '✝',
    'U': '⛎',
    'V': '♈',
    'X': ['❎', '❌'],
    '!!': '‼',
    '!?': '⁉',
    '!': ['❗', '❕'],
    '?': ['❓', '❔'],
}

for a, e in ALTERNATIVES.items():
    if not isinstance(e, list):
        ALTERNATIVES[a] = [e]

async def reactspell(message, text):
    emotes = convert_to_emotes(text)
    for e in emotes:
        try:
            await message.add_reaction(e)
        except:
            pass

def convert_to_emotes_for_react(text):
    return convert_to_emotes(text)

async def spell(context, text):
    emotes = convert_to_emotes(text)
    response = ' '.join(emotes)
    await context.send(response)

def convert_to_emotes_for_message(text):
    text = replace_text_with_alternative_emojis(text)
    return convert_to_emotes(text)

def replace_text_with_alternative_emojis(text):
    text = text.upper()
    for a, emotes in ALTERNATIVES.items():
        if a not in text: continue
        is_letter = a.isalpha() and len(a) == 1
        if is_letter and text.count(a) < 2: continue
        for e in emotes:
            text = replace_nth(text, a, e, 2 if is_letter else 1)
    return text

def convert_to_emotes(text):
    text = text.upper()
    emotes = []
    for c in text.upper():
        if c.isalpha():
            o = ord(c) + REGION_OFFSET
            c = chr(o)
        elif c.isdigit():
            c += KEYCAP
        if c:
            emotes += [c]
    return emotes

def replace_nth(s, sub, repl, n):
    find = s.find(sub)
    i = find != -1
    while find != -1 and i != n:
        find = s.find(sub, find + 1)
        i += 1
    if find >= 0 and i == n:
        return s[:find] + repl + s[find+len(sub):]
    return s