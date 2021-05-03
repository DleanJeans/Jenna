from bs4 import BeautifulSoup
from discord.ext import commands
from urllib.parse import urlparse
from .. import utils

import discord
import textwrap
import re
import colors
import asyncio

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
SPECIAL_WEBSITES = [VREDDIT, GFYCAT, 'twitter', 'imgur', 'youtu']
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

    vreddit_posts = []
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
            extra_msg = await context.send(post.content_url)
            if VREDDIT in post.content_url:
                vreddit_posts += [(msg, extra_msg)]
        
    for msg, extra_msg in vreddit_posts:
        while not extra_msg.embeds:
            await asyncio.sleep(1)
            extra_msg = await extra_msg.channel.fetch_message(extra_msg.id)
            continue
        url = extra_msg.embeds and extra_msg.embeds[0].thumbnail.url
        if url:
            embed = msg.embeds[0]
            embed.set_image(url=url).set_thumbnail(url='')
            await extra_msg.delete()
            await msg.edit(embed=embed)

SAVE_VREDDIT_URL = 'https://savemp4.red/backend.php?url='
REDDIT_POST_REGEX = '(https:\/\/(?:www\.)?reddit\.com\/r\/\w+\/comments\/\w+\/?)'
HREF = 'href'
DOWNLOAD_BUTTON = 'downloadButton'
async def send_preview_for_link(msg):
    reddit_post_links = re.findall(REDDIT_POST_REGEX, msg.content)
    for link in reddit_post_links:
        await msg.channel.trigger_typing()
        rss = await utils.download(link + RSS)
        rss_soup = BeautifulSoup(rss, HTML_PARSER)
        content = rss_soup.find('content').text
        content_soup = BeautifulSoup(content, HTML_PARSER)
        media_link = content_soup.find('span').find('a')[HREF]
        no_media_found = media_link[-1] == '/'
        if no_media_found:
            continue

        if VREDDIT in media_link:
            mp4_link = SAVE_VREDDIT_URL + link + '/'
            mp4_page = await utils.download(mp4_link)
            mp4_soup = BeautifulSoup(mp4_page, HTML_PARSER)
            media_link = mp4_soup.find(class_=DOWNLOAD_BUTTON)[HREF]
    
        await msg.channel.send(media_link)
