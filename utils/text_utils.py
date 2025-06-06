import re

_cyrillic_pat            = re.compile(r'[А-Яа-яЁё]')
_date_pat                = re.compile(r'\b\d{1,2}\.\d{1,2}\.\d{2}(?:\d{2})?\b')
_mention_pat             = re.compile(r'@[^\s]+')
_clean_pat               = re.compile(r'[^\x00-\x7F\u0400-\u04FF]+')
_whitespace_collapse_pat  = re.compile(r'\s+')
_space_before_punct_pat  = re.compile(r'\s+([.,!?;:])')
_dot_sequence_pat        = re.compile(r'\.{2,}')
_word_pat = re.compile(r'\b\w+\b', re.UNICODE)


def contains_cyrillic(text: str) -> bool:
    s = str(text)
    total = len(s)
    if total == 0:
        return False
    # Кількість кириличних символів
    found = _cyrillic_pat.findall(s)
    count_cyr = len(found)
    return (count_cyr / total) > 0.4

def has_minimum_words(text: str, min_words: int = 4) -> bool:
    words = _word_pat.findall(str(text))
    return len(words) >= min_words

def normalize_punctuation(txt: str) -> str:
    return (txt
        .replace('…', '...')
        .replace('❗️', '!')
        .replace('’', "'")
        .replace('‘', "'")
        .replace('/', '.')
        .replace('|', '.')
    )

def strip_dates(txt: str) -> str:
    return _date_pat.sub('', txt)

def strip_mentions(txt: str) -> str:
    def _keep_if_cyr(m: re.Match) -> str:
        return m.group() if _cyrillic_pat.search(m.group()) else ''
    return _mention_pat.sub(_keep_if_cyr, txt)

def drop_non_cyrillic_ascii(txt: str) -> str:
    return _clean_pat.sub('', txt)

def normalize_whitespace_and_dots(txt: str) -> str:
    # collapse any whitespace run to a single space
    txt = _whitespace_collapse_pat.sub(' ', txt)
    # remove space before punctuation
    txt = _space_before_punct_pat.sub(r'\1', txt)
    # collapse two dots → one, three dots stay, four+ → three
    def _dot_cb(m: re.Match) -> str:
        n = len(m.group())
        return '.' if n == 2 else '...'
    txt = _dot_sequence_pat.sub(_dot_cb, txt)
    return txt.strip()

def clean_text(val: str) -> str:
    """
    1. Lowercase
    2. Normalize punctuation
    3. Strip dates
    4. Strip mentions (keeping @cyrillic ones)
    5. Drop any non-Cyrillic/ASCII characters
    6. Collapse whitespace & dot sequences
    """
    txt = str(val).lower()
    txt = normalize_punctuation(txt)
    txt = strip_dates(txt)
    txt = strip_mentions(txt)
    txt = drop_non_cyrillic_ascii(txt)
    txt = normalize_whitespace_and_dots(txt)
    return txt