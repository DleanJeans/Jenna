from bs4 import BeautifulSoup
from ...common import utils
import json
import os

dirname = os.path.dirname(__file__)

DICT_FILE = os.path.join(dirname, 'scramble.json')
word_dict = json.load(open(DICT_FILE))

URLS = [
    'https://www.allscrabblewords.com/unscramble/',
    'https://wordfinder.yourdictionary.com/unscramble/',
]

async def unscramble(scrambled):
    word = lookup(scrambled)
    if word:
        return [word]
    return await lookup_online(scrambled)

def lookup(scrambled):
    length = str(len(scrambled))
    for word in word_dict.get(length, []):
        if sorted(scrambled) == sorted(word):
            return word

async def lookup_online(scrambled):
    for url in URLS:
        anagrams = await lookup_on_site(scrambled, url)
        if anagrams:
            break
    return anagrams
 
async def lookup_on_site(word, url):
    soup = await request_site(word, url)
    anagrams = [a.text.strip() for a in soup('a') if valid_anagram(word, a.text)]
    return anagrams

PARSER = 'html.parser'
async def request_site(word, url):
    url = url + word
    web_content = await utils.request(url)
    soup = BeautifulSoup(web_content, PARSER)
    return soup

def valid_anagram(original, anagram, same_length=True):
    anagram = anagram.strip()
    one_word = ' ' not in anagram
    same_length = len(anagram) == len(original) or not same_length
    return one_word and same_length and anagram.islower()