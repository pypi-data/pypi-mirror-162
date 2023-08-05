# -*- coding: utf-8 -*-
"""Constants for working with Chinese characters."""

from __future__ import unicode_literals

import re
import sys

#: Character code ranges for pertinent CJK ideograph Unicode blocks.
characters = cjk_ideographs = (
    '\u3007'  # Ideographic number zero, see issue #17
    '\u4E00-\u9FFF'  # CJK Unified Ideographs
    '\u3400-\u4DBF'  # CJK Unified Ideographs Extension A
    '\uF900-\uFAFF'  # CJK Compatibility Ideographs
)
if sys.maxunicode > 0xFFFF:
    characters += (
        '\U00020000-\U0002A6DF'  # CJK Unified Ideographs Extension B
        '\U0002A700-\U0002B73F'  # CJK Unified Ideographs Extension C
        '\U0002B740-\U0002B81F'  # CJK Unified Ideographs Extension D
        '\U0002F800-\U0002FA1F'  # CJK Compatibility Ideographs Supplement
    )

#: Character code ranges for the Kangxi radicals and CJK Radicals Supplement.
radicals = (
    '\u2F00-\u2FD5'  # Kangxi Radicals
    '\u2E80-\u2EF3'  # CJK Radicals Supplement
)

#: A string containing Chinese punctuation marks (non-stops).
non_stops = (
    # Fullwidth ASCII variants
    '\uFF02\uFF03\uFF04\uFF05\uFF06\uFF07\uFF08\uFF09\uFF0A\uFF0B\uFF0C\uFF0D'
    '\uFF0F\uFF1A\uFF1B\uFF1C\uFF1D\uFF1E\uFF20\uFF3B\uFF3C\uFF3D\uFF3E\uFF3F'
    '\uFF40\uFF5B\uFF5C\uFF5D\uFF5E\uFF5F\uFF60'

    # Halfwidth CJK punctuation
    '\uFF62\uFF63\uFF64'

    # CJK symbols and punctuation
    '\u3000\u3001\u3003'

    # CJK angle and corner brackets
    '\u3008\u3009\u300A\u300B\u300C\u300D\u300E\u300F\u3010\u3011'

    # CJK brackets and symbols/punctuation
    '\u3014\u3015\u3016\u3017\u3018\u3019\u301A\u301B\u301C\u301D\u301E\u301F'

    # Other CJK symbols
    '\u3030'

    # Special CJK indicators
    '\u303E\u303F'

    # Dashes
    '\u2013\u2014'

    # Quotation marks and apostrophe
    '\u2018\u2019\u201B\u201C\u201D\u201E\u201F'

    # General punctuation
    '\u2026\u2027'

    # Overscores and underscores
    '\uFE4F'

    # Small form variants
    '\uFE51\uFE54'

    # Latin punctuation
    '\u00B7'
)

#: A string of Chinese stops.
stops = (
    '\uFF01'  # Fullwidth exclamation mark
    '\uFF1F'  # Fullwidth question mark
    '\uFF61'  # Halfwidth ideographic full stop
    '\u3002'  # Ideographic full stop
)

#: A string containing all Chinese punctuation.
punctuation = non_stops + stops

# A sentence end is defined by a stop followed by zero or more
# container-closing marks (e.g. quotation or brackets).
_sentence_end_loose = '[%(stops)s][」﹂”』’》）］｝〕〗〙〛〉】]*' % {'stops': stops}

#: A regular expression pattern for a Chinese sentence. A sentence is defined
#: as a series of characters and non-stop punctuation marks followed by a stop
#: and zero or more container-closing punctuation marks (e.g. apostrophe or
# brackets).
sent = sentence = (
                      '[%(characters)s%(radicals)s%(non_stops)s]*%(sentence_end)s'
                  ) % {'characters': characters, 'radicals': radicals, 'non_stops': non_stops,
                       'sentence_end': _sentence_end_loose}

# ---------------------------------------------------------------------------------------------
#: A string of Chinese stops.
stops_loose = (
    '\uFF01'  # Fullwidth exclamation mark
    '\uFF1F'  # Fullwidth question mark
    '\uFF61'  # Halfwidth ideographic full stop
    '\u3002'  # Ideographic full stop
    r' '  # blank
)

#: A string containing all Chinese punctuation.
punctuation_loose = non_stops + stops_loose

# A sentence end is defined by a stop followed by zero or more
# container-closing marks (e.g. quotation or brackets).
_sentence_end = '[%(stops)s][」﹂”』’》）］｝〕〗〙〛〉】]*' % {'stops': stops_loose}
sentence_loose = (
                     '[%(characters)s%(radicals)s%(non_stops)s]*%(sentence_end)s'
                 ) % {'characters': characters, 'radicals': radicals, 'non_stops': non_stops,
                      'sentence_end': _sentence_end}


def cut_sentence_loose(source_text, min_length=4):
    """
    sentence cut
    :param source_text: string
    :return: list
    """
    text = re.findall(sentence_loose, source_text)
    return text


def cut_sentence_strict(source_text):
    """
    sentence cut
    :param source_text: string
    :return: list
    """
    text = re.findall(sentence, source_text)
    return text


zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')


def has_chinese(text):
    match = zh_pattern.search(text)
    return True if match else False


def get_chinese(text, separator=''):
    match = zh_pattern.findall(text)
    _match = separator.join(match)
    return _match


def text_filter(text: str):
    condition = (not text.isdigit()) or text.isalpha() or has_chinese(text)
    return condition


def is_topic(text: str):
    return text.startswith('#')


def cut_sentence_resp(text, min_length=2, drop_topic=True):
    if len(text) > 25:
        _text = re.split(r'[\，\,\！\？\｡\。\～\…\r\n][\」\﹂\”\』\’\》\）\］\｝\〕\〗\〙\〛\〉\】]*', text)
    else:
        _text = re.split(r'[\！\？\｡\。\～\…\r\n][\」\﹂\”\』\’\》\）\］\｝\〕\〗\〙\〛\〉\】]*', text)
    _text = [i.strip() for i in _text]
    _text = [i for i in _text if (len(i) >= min_length and i and text_filter(i))]
    if drop_topic:
        _text = [i for i in _text if not is_topic(i)]
    return _text


if __name__ == '__main__':
    example = """
    <p>春雪飘…    
       雪在慢慢的下
    春天里的桃花雪呀❄️
    三月份的北京
    ​天气一点也不冷
    ​突然间觉得平平安安
    健健康康是多么的重要。</p><p></p>
    """
    # example = """#新周末和坦克去旅行 #坦克路书征途开启\r\n #坦克300\n 雨后穿越安顶山～ 1298-1283-898。10月9日坦克开启路途10km挑战。"""
    # from pick_up_tools.v0.nlp.tools.clean import clean_text
    #
    # example = clean_text(example)

    sen = cut_sentence_strict(example)
    print(sen)
    sen = cut_sentence_loose(example)
    print(sen)
    sen = cut_sentence_resp(example)
    print(example, sen)

    print([get_chinese(i) for i in sen])
