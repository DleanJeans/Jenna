import pytest
from .language_pair import LanguagePair, InvalidLanguageCode, NotLanguagePairFormat


def test_convert_default():
    s = 'fr>en'
    assert_pair_as_str(s, s)


def assert_pair_as_str(input, expected, *, use_default=True):
    pair = LanguagePair.from_string(input, use_default_if_empty=use_default)
    assert str(pair) == expected


def test_use_default_empty_left():
    assert_pair_as_str('>en', 'auto>en')


def test_use_default_empty_right():
    assert_pair_as_str('fr>', 'fr>en')


def test_no_default_empty_right():
    s = 'fr>'
    assert_pair_as_str(s, s, use_default=False)


def test_no_default_empty_left():
    s = '>es'
    assert_pair_as_str(s, s, use_default=False)


def test_invalid_lang_code_raise_error():
    with pytest.raises(InvalidLanguageCode):
        LanguagePair.from_string('>vn')


def test_invalid_format_raise_error():
    with pytest.raises(NotLanguagePairFormat):
        LanguagePair.from_string('en-vi')


def test_override():
    left = LanguagePair.from_string('auto>en')
    right = LanguagePair.from_string('fr>', use_default_if_empty=False)
    merged = left.override(right)
    assert str(merged) == 'fr>en'