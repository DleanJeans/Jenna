REACT = 'React'
PERSIST = 'Persist'

NAMES = [
    'persist',

    'help',
    'cute',
    'dank',
    'preview',

    'images',
    'texts',
    'snipe',
    'emotes',
    'react',
    'misc',
    's',
    'nhoan',
    'games',
    'slash',
    'alpha',
]


def get_full_path(names):
    return ['cogs.' + cog for cog in names]


LIST = get_full_path(NAMES)

LIST += ['jishaku']