from ..common import utils
from bs4 import BeautifulSoup

LSQC_URL = 'http://tracuu.tuvisomenh.com/kinh-dich/la-so-quy-coc-sinh-luc-%s-gio-0-phut-ngay-%s-thang-%s-nam-%s/'
LSQC_CLASSES = ['header', 'left', 'right', 'tu-tu']
YIN = 'kd-hao-am'

def spoiler(s): return f'||{s}||'
def bold(s): return f'**{s}**'

TAB = '    '
YANG_BAR = spoiler(TAB * 10)
HALF_YIN = spoiler(TAB * 4)
YIN_SPACE = TAB * 2
YIN_BAR = HALF_YIN + YIN_SPACE + HALF_YIN
INDENT = TAB * 7
RIGHT_INDENT = TAB * 2

EMOTES = [
    ':yin_yang:',
    ':moneybag:',
    ':handshake:',
    ':ring:',
    ':family_man_girl_boy:',
    ':older_adult:',
    ':briefcase:',
]

class LaSoQuyCoc:
    def __init__(self, laso, details):
        self.laso = laso
        self.details = details
    
    def add_details_as_field(self, embed):
        for emote, (aspect, poem) in zip(EMOTES, self.details):
            embed.add_field(name=f'{emote} {aspect}', value=poem, inline=False)
    
    def format_laso(self):
        title, left, center, right, footer = self.laso
        
        lines = []
        lines += [INDENT + bold(title).center(25, ' ')]
        lines += ['']

        for bar in center:
            bar = YANG_BAR if bar else YIN_BAR
            lines += [INDENT + bar]
            lines += ['']
        
        rtop, rbottom = right.splitlines()
        rjust_width = max(len(rtop), len(rbottom))
        
        lines[4] += RIGHT_INDENT + bold(rtop).rjust(rjust_width, ' ')
        lines[10] += RIGHT_INDENT + bold(rbottom).rjust(rjust_width, ' ')
        lines[7] = bold(left)
        
        cuc, meaning = footer.splitlines()
        lines += [bold(cuc).center(80, ' ')]
        lines += [meaning.center(65, ' ')]

        lines[0] = '﻿' + lines[0]

        return '\n'.join(lines)

async def lookup(dob, birthtime):
    laso, details = await scrape(dob, birthtime)
    return LaSoQuyCoc(laso, details)

def compile_url(dob, birthtime):
    return LSQC_URL % tuple([birthtime] + dob.numbers)

async def scrape(dob, birthtime):
    url = compile_url(dob, birthtime)
    web_content = await utils.download(url)
    soup = BeautifulSoup(web_content, 'html.parser')

    lsqc = soup.find(class_='lsqc')
    title, left, right, footer = find_multiple(lsqc, LSQC_CLASSES)
    center = lsqc(class_='kd-que')[1]
    center = [0 if YIN in q['class'] else 1 for q in center]

    laso = [title, left, center, right, footer]

    table = soup.table
    tbody = table.tbody
    rows = tbody('tr')

    details = []
    for row in rows:
        cols = row('td')
        if len(cols) == 1: continue
        aspect, poem, _ = [c.get_text('\n') for c in cols]
        details += [(aspect, poem)]
    
    cachcuc = soup('div', 'han-nom')[1].get_text('\n').strip()
    cachcuc = cachcuc[cachcuc.index('\n'):].replace('  ', '').strip()
    details.insert(0, ('Cách cục', cachcuc))

    return laso, details

def find_multiple(element, classes):
    return [element.find(class_=c).text.strip() for c in classes]