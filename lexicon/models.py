"""Data models for the Lexicon Lab application."""

from dataclasses import dataclass


@dataclass
class Word:
    """Chinese word model with linguistic properties."""
    
    word: str                       # 词语
    pinyin: str                     # 完整拼音 (带声调)
    pinyin_no_tone: str             # 拼音 (无声调)
    pinyin_initials: str            # 首字母 "xgcl"
    tones: str                      # 声调序列 "1,2,3,4"
    rhyme: str                      # 尾字韵母
    first_char: str                 # 首字
    last_char: str                  # 尾字
    chars: list[str]                # 所有字
    length: int                     # 字数
    definition: str                 # 释义
    source: str | None              # 出处
    example: str | None             # 例句
    category: str                   # 成语/词语/歇后语
    structure: str | None           # AABB/ABAC
    synonyms: list[str] | None      # 近义词
    antonyms: list[str] | None      # 反义词
    frequency: int | None           # 词频
