from bs4 import BeautifulSoup
from discord.ext import commands
from urllib.parse import urlparse, urljoin, urlencode
from .. import utils

import discord
import textwrap
import re
import colors
import asyncio
import json

HTML_PARSER = 'html.parser'
ICON_URL = 'https://www.redditstatic.com/icon.png'
SUB_URL = 'https://www.reddit.com/r/{}/{}/'
RSS = '.rss'
RSS_URL = SUB_URL + RSS
MIN_SUB_NAME = 3
MAX_TEXT = 2000
MAX_TITLE = 250

VREDDIT = 'v.redd.it'
GFYCAT = 'gfycat'
SPECIAL_WEBSITES = [GFYCAT, 'twitter', 'imgur', 'youtu']
def is_special_website(url):
    return any(site in url for site in SPECIAL_WEBSITES)

def subname(sub):
    sub = sub.replace('r/', '').replace('/r/', '')
    if len(sub) < 3 or sub in SORTINGS:
        raise RedditError(f'`r/{sub}` is not a subreddit')
    return sub

TOP = 'top'
SORTINGS = [TOP, 'hot', 'new', 'rising']
def sorting(s):
    s = s.lower()
    for sort in SORTINGS:
        if s[0] in SORTINGS or s in sort:
            return sort
    quoted_sortings = ' '.join([f'`{sort}`' for sort in SORTINGS])
    raise RedditError(f'The sortings are {quoted_sortings}. You can use the first letters.')

def parse_posts(s):
    s = str(s)
    start = 0
    if any(s.endswith(word) for word in ['st', 'nd', 'rd', 'th']):
        posts = int(s[:-2])
        start = posts - 1
    else:
        try: posts = int(s)
        except: raise RedditError(f'`{s}`... posts?')
    return range(start, posts)
posts = parse_posts

PERIODS = ['hour', 'day', 'week', 'month', 'year', 'all']
PERIODS_AS_URL = {
    'now': 'hour',
    'today': 'day',
    'this week': 'week',
    'this month': 'month',
    'this year': 'year',
    'all time': 'all',
}
PERIODS_TO_DISPLAY = { u: p for p, u in PERIODS_AS_URL.items() }

def period(p):
    p = p.lower()
    if p in PERIODS_AS_URL:
        p = PERIODS_AS_URL[p]
    if p not in PERIODS:
        quoted_periods = ', '.join(f'`{p}`' for p in PERIODS_AS_URL)
        aliases = ', '.join(f'`{p}`' for p in PERIODS)
        raise RedditError(f'The possible top periods are {quoted_periods}\nAliases: {aliases}')
    return p

class RedditError(commands.UserInputError):
    def __init__(self, message=None):
        super().__init__(message)

class RedditEntry:
    def __init__(self, sub, title, url, author, thumbnail, content_url, text):
        self.sub = sub
        self.title = title
        self.url = url

        self.titles = textwrap.wrap(title, MAX_TITLE)
        if len(self.titles) > 1:
            self.titles[0] += '...'
            self.titles[1] = '...' + self.titles[1]

        self.author_name = author['name']
        self.author_uri = author['uri']
        self.author = f'[{self.author_name}]({self.author_uri})'

        self.image = content_url if utils.url_is_image(content_url) else ''
        self.thumbnail = thumbnail if not self.image else ''

        self.content_url = ''
        if content_url not in [self.url, self.image]:
            if GFYCAT in content_url:
                content_url = re.sub('\/\w+\/', '/', content_url)
            self.content_url = content_url
            self.content_url_hostname = urlparse(content_url).hostname
            self.content_url_field = f'[{self.content_url_hostname}]({self.content_url})'

        self.text = text
        if len(text) > MAX_TEXT:
            self.text = text[:MAX_TEXT] + '...'
        self.sub_logo = ''
    
    def __str__(self):
        return '\n'.join([self.sub,
        self.title,
        self.url,
        self.thumbnail,
        self.content_url]).replace('\n\n', '\n')
            
def parse_entry(entry):
    content = BeautifulSoup(entry.content.text, HTML_PARSER)
    sub = entry.category['label']
    title = entry.title.text
    url = entry.link[HREF]
    thumbnail = content.img['src'] if content.img else ''

    content_url = content.span.a[HREF] or ''
    text = content.div
    text = text.text if text else ''

    author = entry.author
    author = {
        'name': author.find('name').text,
        'uri': author.uri.text
    }

    return RedditEntry(sub, title, url, author, thumbnail, content_url, text)

def compile_url(sub, sorting, period, link=RSS_URL):
    url = link.format(sub.lower(), sorting)
    if period:
        url += '?t=' + period
    return url

async def download_rss(subreddit, sorting, period):
    url = compile_url(subreddit, sorting, period)
    rss = await utils.download(url)
    errors = [not rss]
    try:
        subname = BeautifulSoup(rss, HTML_PARSER).feed.category['label']
        invalid_subname = ' ' in subname
        errors += [invalid_subname]
    except:
        errors += [True]
    if any(errors):
        raise commands.UserInputError(f'`r\{subreddit}` does not exist')
    return rss

def get_entry_in_rss(rss, index=0, sorting=TOP):
    soup = BeautifulSoup(rss, HTML_PARSER)
    entries = soup('entry')
    
    try:
        entry = entries[index]
    except:
        subreddit = soup.feed.category['label']
        entry_count = len(entries)
        only = 'only ' if entry_count else ''
        raise RedditError(f'`{subreddit}` {only}has **{entry_count}** {sorting} posts today')
    entry = parse_entry(entry)
    sub_logo = soup.feed.logo
    if sub_logo:
        entry.sub_logo = sub_logo.text
    return entry

async def send_posts_in_embeds(context, sub, sorting, posts, period):
    if not isinstance(posts, range):
        posts = parse_posts(posts)
    if sorting is not TOP:
        period = ''
    rss = await download_rss(sub, sorting, period)
    sub_url = compile_url(sub, sorting, period, link=SUB_URL)
    period = PERIODS_TO_DISPLAY.get(period, period).title()

    for i in posts:
        post = get_entry_in_rss(rss, i, sorting)
        title = ' '.join(filter(None, [sorting.title(), f'#{i+1}', period]))
        embed = colors.embed(title=post.titles[0], url=post.url, description=post.text) \
            .set_author(name=f'{title} on ' + post.sub, url=sub_url, icon_url=post.sub_logo) \
            .set_thumbnail(url=post.thumbnail or '') \
            .set_image(url=post.image) \
            .set_footer(text='Reddit', icon_url=ICON_URL)
        if len(post.titles) == 2:
            embed.add_field(name='More Title', value=post.titles[1])
        if post.content_url:
            embed.add_field(name='Link', value=post.content_url_field)
        msg = await context.send(embed=embed)

        if is_special_website(post.content_url):
            await context.send(post.content_url)
        elif VREDDIT in post.content_url or REDDIT_GALLERY in post.content_url:
            await send_media_url_for_post_url(context, post.url)


REDDIT_POST_REGEX = r'(?:\w+\.)?(?:reddit\.com(?:/r/\w+/comments)?|redd\.it)/(\w+)'
HREF = 'href'
JSON = '.json'
MEDIA_URL = 'url_overridden_by_dest'
REDDIT_COM = 'https://www.reddit.com/'
REDDIT_GALLERY = REDDIT_COM + 'gallery/'
MEDIA_METADATA = 'media_metadata'
CROSSPOST_PARENT_LIST = 'crosspost_parent_list'
MAX_URLS_SHOWN = 3

async def detect_post_url_to_send_media_url(context):
    msg = context.message
    await send_media_url_for_post_url(context, msg.content)

async def send_media_url_for_post_url(context, url):
    post_ids = re.findall(REDDIT_POST_REGEX, url)
    media_urls = await get_media_urls_from_post_ids(post_ids)
    if media_urls:
        if len(media_urls) > MAX_URLS_SHOWN:
            omitted_urls = len(media_urls) - MAX_URLS_SHOWN
            media_urls = media_urls[:MAX_URLS_SHOWN] + [f'+ {omitted_urls} more']
        await context.send('\n'.join(media_urls))

async def get_media_urls_from_post_ids(post_ids):
    media_urls = []
    for id in post_ids:
        post_url = urljoin(REDDIT_COM, id)
        json_link = post_url + JSON
        json_data = await utils.download(json_link)
        json_data = json.loads(json_data)
        post_data = json_data[0]['data']['children'][0]['data']
        post_url = urljoin(REDDIT_COM, post_data['permalink'])
        if MEDIA_URL not in post_data:
            continue

        media_url = post_data[MEDIA_URL]
        is_crosspost = media_url.startswith('/r/')
        if is_crosspost:
            continue
        if VREDDIT in media_url:
            media_url = await reddit_tube(post_url)
            if not media_url:
                media_url = await savemp4_red(post_url)
        
        if REDDIT_GALLERY in media_url:
            media_metadata = post_data[MEDIA_METADATA] if MEDIA_METADATA in post_data \
                else post_data[CROSSPOST_PARENT_LIST][0][MEDIA_METADATA]
            for i, (id, data) in enumerate(media_metadata.items()):
                image_data = data['s']
                media_urls.append(f'{i+1}: ' + image_data['u'].replace('&amp;', '&'))
        else:
            media_urls.append(media_url)
    
    return media_urls

from aiocfscrape import CloudflareScraper

REDDIT_TUBE = 'https://www.reddit.tube'
REDDIT_TUBE_SERVICE = 'https://www.reddit.tube/services/get_video?'
async def reddit_tube(post_url):
    async with CloudflareScraper() as session:
        async def cfscrape(url):
            async with session.get(url) as resp:
                return await resp.text()

        page = await cfscrape(REDDIT_TUBE)
        soup = BeautifulSoup(page, HTML_PARSER)
        token_input = soup.find(style="display:none;") or soup.find(type='hidden')
        token_key, token_value = token_input['name'], token_input['value']

        request_link = REDDIT_TUBE_SERVICE + urlencode({'url': post_url, token_key: token_value})
        result = await cfscrape(request_link)
        return json.loads(result).get('url')  

SAVEMP4_RED = 'https://savemp4.red/backend.php?url={}/'
DOWNLOAD_BUTTON = 'downloadButton'
async def savemp4_red(post_url):
    request_link = SAVEMP4_RED.format(post_url)
    page = await utils.download(request_link)
    soup = BeautifulSoup(page, HTML_PARSER)
    mp4_link = soup.find(class_=DOWNLOAD_BUTTON)[HREF]
    return mp4_link