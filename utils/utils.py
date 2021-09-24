import re
import pickle
import joblib
import json
import hjson
import numpy as np
import unicodedata
from pathlib import Path
from typing import Tuple
from pprint import pprint
from string import punctuation
from collections import Counter


REGULAR = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' \
    '0123456789`~!@#$%^&*()_+-=,.<>/?;:\'"[]{}\\|'
SUPERSCRIPTS = 'ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖqʳˢᵗᵘᵛʷˣʸᶻᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻ' \
    '⁰¹²³⁴⁵⁶⁷⁸⁹`~!@#$%^&*⁽⁾_⁺⁻⁼,.<>/?;:\'"[]{}\\|'
SUBSCRIPTS = 'ₐbcdₑfgₕᵢⱼₖₗₘₙₒₚqᵣₛₜᵤᵥwₓyzₐBCDₑFGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥWₓYZ' \
    '₀₁₂₃₄₅₆₇₈₉`~!@#$%^&*₍₎_₊₋₌,.<>/?;:\'"[]{}\\|'

SUPERSCRIPT_MAP = dict(zip(REGULAR, SUPERSCRIPTS))
SUBSCRIPT_MAP = dict(zip(REGULAR, SUBSCRIPTS))
SUPERSCRIPT_INV_MAP = dict(zip(SUPERSCRIPTS, REGULAR))
SUBSCRIPT_INV_MAP = dict(zip(SUBSCRIPTS, REGULAR))

SUBSCRIPT_MAP = str.maketrans(''.join(SUBSCRIPT_MAP.keys()),
                              ''.join(SUBSCRIPT_MAP.values()))
SUBSCRIPT_INV_MAP = str.maketrans(''.join(SUBSCRIPT_INV_MAP.keys()),
                                  ''.join(SUBSCRIPT_INV_MAP.values()))
SUPERSCRIPT_MAP = str.maketrans(''.join(SUPERSCRIPT_MAP.keys()),
                                ''.join(SUPERSCRIPT_MAP.values()))
SUPERSCRIPT_INV_MAP = str.maketrans(''.join(SUPERSCRIPT_INV_MAP.keys()),
                                    ''.join(SUPERSCRIPT_INV_MAP.values()))


def check_file_exists(path: Path):
    if path.is_file():
        return True
    raise FileNotFoundError(f"The file: {path} doesn't exist")


def check_folder_exists(path: Path):
    if path.is_dir():
        return True
    raise FileNotFoundError(f"The dir: {path} doesn't exist")


def load_json(path: Path):
    if check_file_exists(path):
        with open(path, 'r') as fp:
            return json.load(fp)


def load_hjson(path: Path):
    if check_file_exists(path):
        with open(path, 'r') as fp:
            return hjson.load(fp)


def is_blank(text: str) -> bool:
    if text is None:
        return True
    if not isinstance(text, str):
        return True
    return not bool(text and not text.isspace())


def is_not_blank(text: str) -> bool:
    if text is None:
        return False
    if not isinstance(text, str):
        return False
    return bool(text and not text.isspace())


def strip_puncts(text: str, lower=True, strip=True, skip='') -> str:
    '''
    :return text: lowercase, strip and remove
    punctuation: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    '''
    if lower:
        text = text.lower()
    if isinstance(skip, str) and len(skip) > 0 and len(table) > 0:
        puncts = punctuation.translate(str.maketrans('', '', skip))
        table_ = str.maketrans('', '', puncts)
        text = text.translate(table_)
    else:
        text = text.translate(table)
    if strip:
        text = text.strip()
    return str(text)


def superscript(text: str, table=SUPERSCRIPT_MAP) -> str:
    '''f'M{superscript("3")}' -> M³'''
    return str(str(text).translate(table))


def subscript(text: str, table=SUBSCRIPT_MAP) -> str:
    '''f'H{subscript("2")}O' -> H₂O'''
    return str(str(text).translate(table))


def superscript_to_normal(text: str, table=SUPERSCRIPT_INV_MAP) -> str:
    '''f'M{superscript_to_normal("³")}' -> M3'''
    return str(str(text).translate(table))


def subscript_to_normal(text: str, table=SUBSCRIPT_INV_MAP) -> str:
    '''f'H{subscript_to_normal("₂")}O' -> H2O'''
    return str(str(text).translate(table))


def replace_accented(text: str) -> str:
    '''
    :return text: The processed String with Accented Characters Normalized
    '''
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def clean_text(text: str) -> str:
    '''
    :return text: clean text: replace accented chars,
    strip non-ascii chars and punctuations
    '''
    text = subscript_to_normal(text)
    text = superscript_to_normal(text)
    text = replace_accented(text.strip())
    # text = text.encode('ascii', errors='ignore').decode()
    # text = re.sub(r'[^a-zA-Z0-9#\s:$,.()-/@%]', '', text)
    text = ' '.join(text.split())
    return str(text)


def strip_commas(text: str) -> str:
    '''remove , and . chars from the text
       e.g: strip_commas('4,693,687.446') -> '4693687446'
    '''
    if is_not_blank(text):
        table = str.maketrans('', '', ",.")
        text = text.translate(table)
        return str(text.strip())
    return text


def np_iter(iterable, dtype='U100000'):  # pragma: no cover <--
    return np.fromiter(iterable, dtype)


def list_get(lst: list, idx: int, default='NA'):
    '''Safe get for list without raising IndexErrors'''
    try:
        return lst[idx]
    except IndexError:
        return default
