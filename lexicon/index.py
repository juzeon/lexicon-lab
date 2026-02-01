"""Fast lookup indexes for Chinese word database."""

from collections import Counter, defaultdict
from lexicon.models import Word


class LexiconIndex:
    """Provides fast lookups for Chinese words using multiple indexes."""
    
    def __init__(self, words: list[Word]):
        self.words = words
        
        self.by_first_char: dict[str, list[int]] = {}
        self.by_last_char: dict[str, list[int]] = {}
        self.by_char: dict[str, list[int]] = {}
        self.by_pinyin_initials: dict[str, list[int]] = {}
        self.by_pinyin_no_tone: dict[str, list[int]] = {}
        self.by_rhyme: dict[str, list[int]] = {}
        self.by_length: dict[int, list[int]] = {}
        self.by_category: dict[str, list[int]] = {}
        self.by_structure: dict[str, list[int]] = {}
        self.by_char_pinyin: dict[str, set[str]] = {}
        self.by_similar_pinyin: dict[str, set[str]] = {}
        
        self.char_freq_start: Counter = Counter()
        self.char_freq_end: Counter = Counter()
        self.char_freq_all: Counter = Counter()
        
        self._build_indexes()
    
    @staticmethod
    def _is_chinese_char(char: str) -> bool:
        if not char or len(char) != 1:
            return False
        code_point = ord(char)
        return (
            (0x4E00 <= code_point <= 0x9FFF) or
            (0x3400 <= code_point <= 0x4DBF) or
            (0x20000 <= code_point <= 0x2A6DF) or
            (0x2A700 <= code_point <= 0x2B73F) or
            (0x2B740 <= code_point <= 0x2B81F) or
            (0x2B820 <= code_point <= 0x2CEAF) or
            (0x2CEB0 <= code_point <= 0x2EBEF) or
            (0xF900 <= code_point <= 0xFAFF) or
            (0x2F800 <= code_point <= 0x2FA1F)
        )
    
    def _build_indexes(self) -> None:
        from lexicon.pinyin_utils import get_similar_pinyin
        
        by_first_char = defaultdict(list)
        by_last_char = defaultdict(list)
        by_char = defaultdict(list)
        by_pinyin_initials = defaultdict(list)
        by_pinyin_no_tone = defaultdict(list)
        by_rhyme = defaultdict(list)
        by_length = defaultdict(list)
        by_category = defaultdict(list)
        by_structure = defaultdict(list)
        by_char_pinyin = defaultdict(set)
        by_similar_pinyin = defaultdict(set)
        
        for idx, word in enumerate(self.words):
            by_first_char[word.first_char].append(idx)
            self.char_freq_start[word.first_char] += 1
            
            by_last_char[word.last_char].append(idx)
            self.char_freq_end[word.last_char] += 1
            
            syllables = word.pinyin_no_tone.split() if word.pinyin_no_tone else []
            for i, char in enumerate(word.chars):
                by_char[char].append(idx)
                self.char_freq_all[char] += 1
                
                if i < len(syllables) and self._is_chinese_char(char):
                    py_syllable = syllables[i]
                    by_char_pinyin[py_syllable].add(char)
                    
                    similar_pys = get_similar_pinyin(py_syllable)
                    for similar_py in similar_pys:
                        by_similar_pinyin[py_syllable].add(similar_py)
            
            by_pinyin_initials[word.pinyin_initials].append(idx)
            by_pinyin_no_tone[word.pinyin_no_tone].append(idx)
            by_rhyme[word.rhyme].append(idx)
            by_length[word.length].append(idx)
            by_category[word.category].append(idx)
            
            if word.structure:
                by_structure[word.structure].append(idx)
        
        self.by_first_char = dict(by_first_char)
        self.by_last_char = dict(by_last_char)
        self.by_char = dict(by_char)
        self.by_pinyin_initials = dict(by_pinyin_initials)
        self.by_pinyin_no_tone = dict(by_pinyin_no_tone)
        self.by_rhyme = dict(by_rhyme)
        self.by_length = dict(by_length)
        self.by_category = dict(by_category)
        self.by_structure = dict(by_structure)
        self.by_char_pinyin = dict(by_char_pinyin)
        self.by_similar_pinyin = dict(by_similar_pinyin)
