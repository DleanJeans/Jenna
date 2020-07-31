from bs4 import BeautifulSoup
from datetime import datetime
from .. import utils
from ..emotes import utils as emutils 
from discord.ext import commands
from dataclasses import dataclass

import discord
import time
import pycountry
import colors
import asyncio
from flag import flag as get_flag

URL = 'https://www.worldometers.info/coronavirus/'
UPDATE_INTERVAL = 5 * 60

class CoronaStatus:
    def __init__(self):
        self.data = []
        self.last_update = 0
        self.is_downloading = False
    
    async def update(self):
        if self.should_update():
            self.last_update = time.time()
            await self.download_data()
        while self.is_downloading:
            await asyncio.sleep(1)
    
    def should_update(self):
        now = time.time()
        data_age = now - self.last_update
        return data_age > UPDATE_INTERVAL

    async def download_data(self):
        self.is_downloading = True
        data = []

        web_content = await utils.download(URL)
        soup = BeautifulSoup(web_content, 'html.parser')
        table = soup.table

        for tbody in table('tbody')[::-1]:
            rows = tbody('tr')
            for row in rows:
                cols = row('td')
                cols = [c.text.strip() for c in cols]
                country = [c for c in cols]
                
                name = country[1]
                if not name:
                    continue
                elif name == 'Total:':
                    country[1] = country[-1]
                elif name in COUNTRY_RENAMES:
                    country[1] = COUNTRY_RENAMES[name]

                for i, value in enumerate(country):
                    if value != 'N/A':
                        value = str(value or 0).replace('+', '').replace(',', '')
                    try: country[i] = int(value)
                    except: pass

                data += [country]
        
        self.data = data
        self.is_downloading = False

COUNTRY_RENAMES = {
    'S. Korea': 'South Korea',
}
COUNTRIES_OF_INTEREST = ['Vietnam', 'USA', 'Singapore', 'Germany', 'Canada', 'Australia', 'Malaysia', 'Netherlands']

FLAG_EMOTES_BY_COUNTRY = {}
for name in COUNTRIES_OF_INTEREST:
    alpha2 = pycountry.countries.search_fuzzy(name)[0].alpha_2
    FLAG_EMOTES_BY_COUNTRY[name] = ':flag_%s:' % alpha2.lower()

WORLD = 'World'
GLOBE = '🌏'
COUNTRIES_OF_INTEREST.insert(0, WORLD)
FLAG_EMOTES_BY_COUNTRY[WORLD] = GLOBE

TOTAL_CASES = 'Total Cases'
NEW_CASES = 'New Cases'
TOTAL_DEATHS = 'Total Deaths'
NEW_DEATHS = 'New Deaths'
RECOVERED_EMOTE = ':recovered:'
RECOVERED = 'Recovered'
EXPLANATION = f''':microbe: **{TOTAL_CASES}** (+{NEW_CASES})
:skull: **{TOTAL_DEATHS}** (+{NEW_DEATHS})
{RECOVERED_EMOTE} **{RECOVERED}**
__
'''

@dataclass
class CustomEmotes:
    recovered: str

def set_emotes(recovered):
    global emotes
    emotes = CustomEmotes(recovered)

def compile_stats(country_data):
    total_cases, new_cases, total_deaths, new_deaths, recovered = map(comma, country_data[2:7])
    new_cases = plus(new_cases)
    new_deaths = plus(new_deaths)
    return (
        f':microbe: **{total_cases}** {new_cases}\n'
        f':skull: **{total_deaths}** {new_deaths}\n'
        f'{emotes.recovered} **{recovered}**\n'
        '__' )

def comma(number):
    return f'{number:,}' if type(number) is int else number

def plus(number, hide_if_none=True):
    return '' if number == '0' and hide_if_none else f'(+{number})'

TITLE = 'Worldometer Coronavirus Update'
def create_empty_embed():
    return colors.embed(title=TITLE, url=URL, description='Downloading data...')

def embed_countries(data):
    embed = create_empty_embed() 
    embed.description = EXPLANATION.replace(RECOVERED_EMOTE, emotes.recovered)
    embed.timestamp = datetime.now().astimezone()

    for country_data in data:
        name = country_data[1]
        if name not in COUNTRIES_OF_INTEREST: continue

        flag_emote = FLAG_EMOTES_BY_COUNTRY[name]
        country_name = f'{flag_emote} {name}'
        content = compile_stats(country_data)

        embed.add_field(name=country_name, value=content)
    
    return embed

def percent(num, denom, brackets=False):
    if type(num) == str or num == 0 or denom == 0: return ''
    number = num / denom * 100
    num_str = f'{number:.1g}' if number < 1 else f'{number:.1f}'
    output = f'{num_str}%' if number else ''
    if output and brackets:
        output = f'[{output}]'
    return output

def embed_region(data, region):
    country_data, alpha2 = get_country_data_fuzzy(data, region)
    if not country_data:
        raise commands.UserInputError('Country not found!')
    
    flag = country_code = '🚩'
    if country_data and country_data[-1] == 'All':
        flag = country_code = GLOBE
    if alpha2:
        flag = ':flag_{}:'.format(alpha2.lower())
        country_code = get_flag(alpha2.upper()) if alpha2 else flag
    flag_image = emutils.get_url(country_code)[0]
    
    wtotal_cases, _, wtotal_deaths = data[0][2:5]
    name, total_cases, new_cases, total_deaths, new_deaths, recovered, _, active_cases, critical, cases_per_1m, deaths_per_1m = country_data[1:12]

    recovered_percent = percent(recovered, total_cases, brackets=True)
    active_percent = percent(active_cases, total_cases, brackets=True)
    critical_percent = percent(critical, total_cases, brackets=True)

    wcases_percent = percent(total_cases, wtotal_cases)
    wdeaths_percent = percent(total_deaths, wtotal_deaths)
    deaths_percent = percent(total_deaths, total_cases)
    cases_percent = percent(cases_per_1m, 10**6)
    deaths_pop_percent = percent(deaths_per_1m, 10**6)

    is_world = country_data[-1] == 'All'
    wcases_percent = f'{GLOBE} {wcases_percent}' if wcases_percent and not is_world else ''
    wdeaths_percent = f'{GLOBE} {wdeaths_percent}' if wdeaths_percent and not is_world else ''
    deaths_percent = f':microbe: {deaths_percent}' if deaths_percent else ''
    cases_percent = f'{flag} {cases_percent}' if cases_percent else ''
    deaths_pop_percent = f'{flag} {deaths_pop_percent}' if deaths_pop_percent else ''

    total_cases, new_cases, total_deaths, new_deaths, recovered, _, active_cases, critical = map(comma, country_data[2:10])
    new_cases = plus(new_cases, hide_if_none=False)
    new_deaths = plus(new_deaths, hide_if_none=False)
    
    cases_percentages = '\n'.join(filter(None, [wcases_percent, cases_percent]))
    if cases_percentages: cases_percentages = '\n' + cases_percentages
    deaths_percentages = '\n'.join(filter(None, [wdeaths_percent, deaths_pop_percent, deaths_percent]))
    if deaths_percentages: deaths_percentages = '\n' + deaths_percentages

    explanation = '\n'.join(filter(None, (
        f'{GLOBE} % Global Cases' if flag != GLOBE else '',
        f'{flag} % Population' if flag in cases_percent + deaths_pop_percent else '',
        f':microbe: % Total Cases' if ':microbe:' in deaths_percent else '',
    )))

    title = f'Coronavirus cases for {name}'
    embed = colors.embed(title=title, url=URL, description=explanation) \
        .add_field(name=f'{TOTAL_CASES}', value=f'**{total_cases}** {new_cases}{cases_percentages}') \
        .add_field(name=f'{TOTAL_DEATHS}', value=f'**{total_deaths}** {new_deaths}{deaths_percentages}') \
        .add_field(name=f'{RECOVERED}', value=f'**{recovered}** {recovered_percent}', inline=False) \
        .add_field(name=f'Active Cases', value=f'**{active_cases}** {active_percent}') \
        .add_field(name=f'Critical', value=f'**{critical}** {critical_percent}') \
        .set_thumbnail(url=flag_image)  
    embed.timestamp = datetime.now().astimezone()
    return embed

CONTINENTS = ['World', 'All', 'Europe', 'North America', 'South America', 'Asia', 'Africa', 'Oceania']
CUSTOM_SEARCH_TERMS = {
    'south korea': 'KOR',
    'uk': 'GB',
}

def get_country_data_fuzzy(data, region):
    country = None
    if region.title() not in CONTINENTS:
        term = CUSTOM_SEARCH_TERMS.get(region.lower())
        if not term:
            term = region
        try:
            countries = pycountry.countries.search_fuzzy(term)
            country = countries[0]
        except:
            pass
    
    possible_names = [region]
    if country:
        acronym = ''.join(word[0] for word in country.name.split())
        official_name = getattr(country, 'official_name', '')
        common_name = getattr(country, 'common_name', '')
        possible_names += [country.alpha_2, country.alpha_3, country.name, official_name, common_name, acronym]
    possible_names = [n.lower() for n in possible_names]

    def match_name(c):
        name = str(c[1]).lower()
        return name in possible_names
    country_data = discord.utils.find(match_name, data)
    alpha2 = country.alpha_2 if country else ''
    if region.lower() == 'europe': alpha2 = 'EU'

    return country_data, alpha2