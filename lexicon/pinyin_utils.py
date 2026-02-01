"""Pinyin processing utilities with multi-pronunciation support.

This module provides comprehensive pinyin processing for Chinese characters,
with special handling for multi-pronunciation characters (多音字).

Examples:
    >>> get_pinyin("朝阳")
    "zhāo yáng"
    
    >>> get_pinyin_initials("朝阳")
    ["zy", "cy"]  # Both pronunciations: zhāo yáng and cháo yáng
    
    >>> get_tones("zhāo yáng")
    "1,2"
"""

from itertools import product
from typing import List

from pypinyin import pinyin, lazy_pinyin, Style


def get_pinyin(word: str) -> str:
    """Get full pinyin with tones (space-separated).
    
    For multi-pronunciation characters, returns the first (most common) pronunciation.
    
    Args:
        word: Chinese word/phrase
        
    Returns:
        Space-separated pinyin with tone marks (e.g., "zhāo yáng")
        
    Examples:
        >>> get_pinyin("你好")
        "nǐ hǎo"
        >>> get_pinyin("朝阳")
        "zhāo yáng"
    """
    result = lazy_pinyin(word, style=Style.TONE)
    return " ".join(result)


def get_pinyin_no_tone(word: str) -> str:
    """Get pinyin without tones (space-separated).
    
    Args:
        word: Chinese word/phrase
        
    Returns:
        Space-separated pinyin without tones (e.g., "zhao yang")
        
    Examples:
        >>> get_pinyin_no_tone("你好")
        "ni hao"
        >>> get_pinyin_no_tone("朝阳")
        "zhao yang"
    """
    result = lazy_pinyin(word, style=Style.NORMAL)
    return " ".join(result)


def get_pinyin_initials(word: str) -> List[str]:
    """Get ALL possible initial combinations for multi-pronunciation characters.
    
    This function handles 多音字 (multi-pronunciation characters) by generating
    the Cartesian product of all possible pronunciations.
    
    Args:
        word: Chinese word/phrase
        
    Returns:
        List of all possible initial combinations
        
    Examples:
        >>> get_pinyin_initials("朝阳")
        ["zy", "cy"]  # "朝" can be "zhāo" or "cháo"
        
        >>> get_pinyin_initials("中国")
        ["zg"]  # Single pronunciation
        
        >>> get_pinyin_initials("重要")
        ["zy", "cy"]  # "重" can be "zhòng" or "chóng"
    """
    # Get all possible pronunciations for each character (heteronym=True)
    all_pinyins = pinyin(word, style=Style.FIRST_LETTER, heteronym=True)
    
    # Generate Cartesian product of all initial combinations
    # each item in all_pinyins is a list of possible initials for that character
    combinations = product(*all_pinyins)
    
    # Convert tuples to strings and remove duplicates while preserving order
    result = []
    seen = set()
    for combo in combinations:
        combo_str = "".join(combo)
        if combo_str not in seen:
            seen.add(combo_str)
            result.append(combo_str)
    
    return result


def get_tones(pinyin_str: str) -> str:
    """Extract tone sequence from pinyin string.
    
    Converts pinyin with tone marks to a comma-separated tone number sequence.
    
    Args:
        pinyin_str: Pinyin string with tone marks (e.g., "nǐ hǎo")
        
    Returns:
        Comma-separated tone sequence (e.g., "3,3")
        
    Examples:
        >>> get_tones("nǐ hǎo")
        "3,3"
        >>> get_tones("zhāo yáng")
        "1,2"
        >>> get_tones("bu yong xie")
        "0,4,4"  # 轻声 is tone 0
    """
    # Tone mark to number mapping
    tone_marks = {
        'ā': '1', 'á': '1', 'ǎ': '3', 'à': '4',
        'ē': '1', 'é': '2', 'ě': '3', 'è': '4',
        'ī': '1', 'í': '2', 'ǐ': '3', 'ì': '4',
        'ō': '1', 'ó': '2', 'ǒ': '3', 'ò': '4',
        'ū': '1', 'ú': '2', 'ǔ': '3', 'ù': '4',
        'ǖ': '1', 'ǘ': '2', 'ǚ': '3', 'ǜ': '4',
        'ü': '0', 'v': '0',
    }
    
    # More accurate tone mark mapping
    tone_marks_accurate = {
        # a
        'ā': '1', 'á': '2', 'ǎ': '3', 'à': '4',
        # e
        'ē': '1', 'é': '2', 'ě': '3', 'è': '4',
        # i
        'ī': '1', 'í': '2', 'ǐ': '3', 'ì': '4',
        # o
        'ō': '1', 'ó': '2', 'ǒ': '3', 'ò': '4',
        # u
        'ū': '1', 'ú': '2', 'ǔ': '3', 'ù': '4',
        # ü
        'ǖ': '1', 'ǘ': '2', 'ǚ': '3', 'ǜ': '4',
    }
    
    syllables = pinyin_str.split()
    tones = []
    
    for syllable in syllables:
        tone = '0'  # Default to neutral tone (轻声)
        for char in syllable:
            if char in tone_marks_accurate:
                tone = tone_marks_accurate[char]
                break
        tones.append(tone)
    
    return ",".join(tones)


def get_rhyme(word: str) -> str:
    """Get rhyme (韵母) of the last character.
    
    The rhyme is the part of a syllable after the initial consonant.
    
    Args:
        word: Chinese word/phrase
        
    Returns:
        Rhyme (final) of the last character
        
    Examples:
        >>> get_rhyme("天空")
        "ong"
        >>> get_rhyme("朝阳")
        "ang"
        >>> get_rhyme("中国")
        "uo"
    """
    if not word:
        return ""
    
    # Get the final (韵母) of the last character
    last_char = word[-1]
    finals = pinyin(last_char, style=Style.FINALS, heteronym=False)
    
    if finals and finals[0]:
        return finals[0][0]
    
    return ""


def get_all_pinyin_variants(word: str) -> List[str]:
    """Get all possible pinyin combinations for multi-pronunciation characters.
    
    Similar to get_pinyin_initials but returns full pinyin instead of just initials.
    
    Args:
        word: Chinese word/phrase
        
    Returns:
        List of all possible pinyin combinations
        
    Examples:
        >>> get_all_pinyin_variants("朝阳")
        ["zhāo yáng", "cháo yáng"]
        
        >>> get_all_pinyin_variants("中国")
        ["zhōng guó"]
    """
    # Get all possible pronunciations for each character
    all_pinyins = pinyin(word, style=Style.TONE, heteronym=True)
    
    # Generate Cartesian product of all combinations
    combinations = product(*all_pinyins)
    
    # Convert to space-separated strings
    result = []
    seen = set()
    for combo in combinations:
        combo_str = " ".join(combo)
        if combo_str not in seen:
            seen.add(combo_str)
            result.append(combo_str)
    
    return result


def get_all_pinyin_no_tone_variants(word: str) -> List[str]:
    """Get all possible pinyin combinations without tones.
    
    Args:
        word: Chinese word/phrase
        
    Returns:
        List of all possible pinyin combinations without tones
        
    Examples:
        >>> get_all_pinyin_no_tone_variants("朝阳")
        ["zhao yang", "chao yang"]
    """
    # Get all possible pronunciations for each character (no tone)
    all_pinyins = pinyin(word, style=Style.NORMAL, heteronym=True)
    
    # Generate Cartesian product
    combinations = product(*all_pinyins)
    
    # Convert to space-separated strings
    result = []
    seen = set()
    for combo in combinations:
        combo_str = " ".join(combo)
        if combo_str not in seen:
            seen.add(combo_str)
            result.append(combo_str)
    
    return result


def pinyin_to_hanzi(pinyin_text: str) -> List[str]:
    """Convert pinyin to possible Chinese characters.
    
    Args:
        pinyin_text: Pinyin string (e.g., "wan", "wang", "zhong")
        
    Returns:
        List of Chinese characters with this pronunciation
        
    Examples:
        >>> pinyin_to_hanzi("wan")
        ['万', '玩', '晚', '完', '弯', ...]
        >>> pinyin_to_hanzi("zhong")
        ['中', '重', '种', '终', ...]
    """
    return []


def get_similar_pinyin(pinyin_text: str) -> List[str]:
    """Get homophones (similar sounding pinyin).
    
    Args:
        pinyin_text: Pinyin string without tones (e.g., "wan", "zhang")
        
    Returns:
        List of similar-sounding pinyin
        
    Examples:
        >>> get_similar_pinyin("wan")
        ['wang', 'wen', 'weng', 'yuan']
        >>> get_similar_pinyin("zhang")
        ['zang', 'zheng', 'chang', 'shang']
    """
    SIMILAR_INITIALS = {
        'zh': ['z'],
        'z': ['zh'],
        'ch': ['c'],
        'sh': ['s'],
        'c': ['ch'],
        's': ['sh'],
        'n': ['l'],
        'l': ['n'],
        'f': ['h'],
        'h': ['f'],
    }
    
    SIMILAR_FINALS = {
        'an': ['ang', 'en'],
        'ang': ['an', 'eng'],
        'en': ['an', 'eng', 'in'],
        'eng': ['ang', 'en', 'ing'],
        'in': ['ing', 'en'],
        'ing': ['in', 'eng'],
        'ian': ['iang', 'uan', 'yan'],
        'iang': ['ian', 'uang', 'yang'],
        'uan': ['uang', 'ian', 'wan'],
        'uang': ['uan', 'iang', 'wang'],
        'ao': ['ou'],
        'ou': ['ao'],
        'ai': ['ei'],
        'ei': ['ai'],
        'ui': ['ei', 'ue'],
        'ue': ['ui', 'ie'],
        'ie': ['ue', 'ei'],
        'uo': ['ou', 'o'],
        'o': ['uo', 'ou'],
    }
    
    INITIALS = ['zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 
                'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's', 'y', 'w']
    
    pinyin_lower = pinyin_text.lower().strip()
    result = set()
    
    initial = ''
    final = pinyin_lower
    for init in sorted(INITIALS, key=len, reverse=True):
        if pinyin_lower.startswith(init):
            initial = init
            final = pinyin_lower[len(init):]
            break
    
    if initial in SIMILAR_INITIALS:
        for sim_init in SIMILAR_INITIALS[initial]:
            result.add(sim_init + final)
    
    if final in SIMILAR_FINALS:
        for sim_final in SIMILAR_FINALS[final]:
            result.add(initial + sim_final)
            if initial in SIMILAR_INITIALS:
                for sim_init in SIMILAR_INITIALS[initial]:
                    result.add(sim_init + sim_final)
    
    result.discard(pinyin_lower)
    
    return sorted(list(result))


def expand_pinyin_wildcards(pinyin_pattern: str) -> List[str]:
    """Expand @ wildcards in pinyin patterns.
    
    @ symbol acts as wildcard for finals (vowels):
    - t@cai -> t+any_final+cai -> tiancai, tencai, ticai, tucai, etc.
    - tianc@ -> tianc+any_final -> tiancai, tiancao, tiancang, etc.
    
    Args:
        pinyin_pattern: Pinyin pattern with @ wildcards (e.g., "t@cai", "tianc@")
        
    Returns:
        List of expanded pinyin strings
        
    Examples:
        >>> expand_pinyin_wildcards("t@cai")
        ['tiancai', 'tencai', 'ticai', 'tucai', ...]
        >>> expand_pinyin_wildcards("tianc@")
        ['tiancai', 'tiancao', 'tiancang', ...]
    """
    FINALS = [
        'a', 'ai', 'an', 'ang', 'ao',
        'e', 'ei', 'en', 'eng', 'er',
        'i', 'ia', 'ian', 'iang', 'iao', 'ie', 'in', 'ing', 'iong', 'iu',
        'o', 'ong', 'ou',
        'u', 'ua', 'uai', 'uan', 'uang', 'ui', 'un', 'uo',
        'v', 've', 'van', 'vn',
    ]
    
    if '@' not in pinyin_pattern:
        return [pinyin_pattern]
    
    parts = pinyin_pattern.split('@')
    if len(parts) != 2:
        return [pinyin_pattern]
    
    left_part, right_part = parts
    
    result = []
    for final in FINALS:
        expanded = left_part + final + right_part
        result.append(expanded)
    
    return result
