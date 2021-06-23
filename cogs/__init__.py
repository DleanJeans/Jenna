REACT = 'React'
PERSIST = 'Persist'

NAMES = [
    'persist',
    'dank',
    'help',
    'alpha',
    'react',
    'cute',
    'preview',

    'texts',
    'images',
    's',
    'snipe',
    'emotes',
    'games',

    'nhoan',
    'misc'
]


def get_full_path(names):
    return ['cogs.' + cog for cog in names]


LIST = get_full_path(NAMES)
