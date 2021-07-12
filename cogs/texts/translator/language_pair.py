import re
from cogs.common.api.googledict import SUPPORTED_LANGS


class NotLanguagePairFormat(ValueError):
    pass


class InvalidLanguageCode(ValueError):
    pass


REGEX = r'([\w-]*)>([\w-]*)'
INVALID_FORMAT = '`{}` not in lang>lang format!'
INVALID_LANGUAGE_CODE = '{} is not a valid language code!'
DEFAULT_SRC = 'auto'
DEFAULT_DEST = 'en'


class LanguagePair:
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    @classmethod
    def from_string(cls, string, *, use_default_if_empty=True):
        matches = re.findall(REGEX, string)
        raise_error_if_invalid_format(string, matches)
        src, dest = matches[0]
        if use_default_if_empty:
            src, dest = use_default(src, dest)
        src, dest = map(apply_zh_fixes, [src, dest])
        raise_error_if_any_not_supported([src, dest])
        return cls(src, dest)

    @classmethod
    def default(cls):
        return cls(DEFAULT_SRC, DEFAULT_DEST)

    def override(self, pair):
        return LanguagePair(pair.src or self.src, pair.dest or self.dest)

    def as_list(self):
        return [self.src, self.dest]

    def __str__(self):
        return f'{self.src}>{self.dest}'

    def __repr__(self) -> str:
        return f'LanguagePair({self})'


def apply_zh_fixes(lang):
    lang = lang.replace('_', '-')
    if lang.startswith('zh') and lang not in SUPPORTED_LANGS:
        return 'zh-cn'
    return lang


def raise_error_if_invalid_format(string, regex_matches):
    if not regex_matches:
        raise NotLanguagePairFormat(INVALID_FORMAT.format(string))


def use_default(src, dest):
    return src or DEFAULT_SRC, dest or DEFAULT_DEST


def raise_error_if_any_not_supported(langs):
    for lang in langs:
        raise_error_if_not_supported(lang)


def raise_error_if_not_supported(lang):
    if lang and lang not in SUPPORTED_LANGS:
        raise InvalidLanguageCode(INVALID_LANGUAGE_CODE.format(lang))
