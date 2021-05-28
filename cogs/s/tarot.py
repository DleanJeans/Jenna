import os
import posixpath

names_file = posixpath.join(os.path.dirname(__file__), 'tarot.txt')
NAMES = open(names_file).read()

MAJORS, MINORS, FACES = [block.splitlines() for block in NAMES.split('\n\n')]
RANKS = [FACES[0]] + [i for i in range(2, 11)] + FACES[1:]

ORIGIN = 'https://www.tarotcardmeanings.net'

IMG_PATH = 'images/tarotcards-large/'
MAJOR_PATH = 'majorarcana/'
MINOR_PATH = 'minorarcana/'

MAJOR_IMG = 'tarot-{}.jpg'
MINOR_IMG = 'tarot-{}-{:02d}.jpg'
MEANING_PAGE = 'tarot-{}.htm'
THE = 'The '
OF = ' of '

CARDS = []

for card in MAJORS:
    name = THE + card.title()
    url_name = card.replace(' ', '')
    image = posixpath.join(ORIGIN, IMG_PATH, MAJOR_IMG.format(url_name))
    url = posixpath.join(ORIGIN, MAJOR_PATH, MEANING_PAGE.format(url_name))
    CARDS += [[name, image, url]]

for suit in MINORS:
    for i, rank in enumerate(RANKS):
        name = str(rank).title() + OF + suit.title()
        image = posixpath.join(ORIGIN, IMG_PATH, MINOR_IMG.format(suit, i + 1))
        url = posixpath.join(ORIGIN, MINOR_PATH, MEANING_PAGE.format(suit))
        CARDS += [[name, image, url]]