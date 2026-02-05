"""Tests for search engine functionality."""

import pytest
from lexicon.models import Word
from lexicon.search import SearchEngine
from lexicon.index import LexiconIndex
from pathlib import Path


@pytest.fixture
def sample_words():
    """Create sample words for testing."""
    return [
        Word(
            word="中国",
            pinyin="zhōng guó",
            pinyin_no_tone="zhong guo",
            pinyin_initials="zg",
            tones="1,2",
            rhyme="uo",
            first_char="中",
            last_char="国",
            chars=["中", "国"],
            length=2,
            definition="东亚国家",
            source=None,
            example=None,
            category="词语",
            structure=None,
            synonyms=None,
            antonyms=None,
            frequency=None,
        ),
        Word(
            word="天长地久",
            pinyin="tiān cháng dì jiǔ",
            pinyin_no_tone="tian chang di jiu",
            pinyin_initials="tcdj",
            tones="1,2,4,3",
            rhyme="iu",
            first_char="天",
            last_char="久",
            chars=["天", "长", "地", "久"],
            length=4,
            definition="形容时间悠久",
            source="老子",
            example="他们的爱情天长地久",
            category="成语",
            structure="ABCD",
            synonyms=None,
            antonyms=None,
            frequency=None,
        ),
        Word(
            word="高高兴兴",
            pinyin="gāo gāo xìng xìng",
            pinyin_no_tone="gao gao xing xing",
            pinyin_initials="ggxx",
            tones="1,1,4,4",
            rhyme="ing",
            first_char="高",
            last_char="兴",
            chars=["高", "高", "兴", "兴"],
            length=4,
            definition="快乐的样子",
            source=None,
            example="孩子们高高兴兴地玩耍",
            category="词语",
            structure="AABB",
            synonyms=None,
            antonyms=None,
            frequency=None,
        ),
        Word(
            word="一心一意",
            pinyin="yī xīn yī yì",
            pinyin_no_tone="yi xin yi yi",
            pinyin_initials="yxyy",
            tones="1,1,1,4",
            rhyme="i",
            first_char="一",
            last_char="意",
            chars=["一", "心", "一", "意"],
            length=4,
            definition="专心致志",
            source=None,
            example="他一心一意地工作",
            category="成语",
            structure="ABAC",
            synonyms=None,
            antonyms=None,
            frequency=None,
        ),
        Word(
            word="研究研究",
            pinyin="yán jiū yán jiū",
            pinyin_no_tone="yan jiu yan jiu",
            pinyin_initials="yjyj",
            tones="2,1,2,1",
            rhyme="iu",
            first_char="研",
            last_char="究",
            chars=["研", "究", "研", "究"],
            length=4,
            definition="仔细思考",
            source=None,
            example="我需要研究研究这个问题",
            category="词语",
            structure="ABAB",
            synonyms=None,
            antonyms=None,
            frequency=None,
        ),
    ]


@pytest.fixture
def test_index(sample_words):
    """Create index from sample words."""
    return LexiconIndex(sample_words)


@pytest.fixture
def mock_search_engine(sample_words):
    """Create mock SearchEngine with sample words."""
    engine = SearchEngine.__new__(SearchEngine)
    engine.words = sample_words
    engine.index = LexiconIndex(sample_words)
    return engine


class TestSearchByLength:
    """Test search by word length."""

    def test_search_length_2(self, mock_search_engine):
        """Test search for 2-character words."""
        results = mock_search_engine.search(length=2)
        assert len(results) == 1
        assert results[0].word == "中国"

    def test_search_length_4(self, mock_search_engine):
        """Test search for 4-character words."""
        results = mock_search_engine.search(length=4)
        assert len(results) == 4

    def test_search_length_no_match(self, mock_search_engine):
        """Test search for length that doesn't exist."""
        results = mock_search_engine.search(length=10)
        assert len(results) == 0


class TestSearchByCategory:
    """Test search by word category."""

    def test_search_category_idiom(self, mock_search_engine):
        """Test search for idioms."""
        results = mock_search_engine.search(category="成语")
        assert len(results) == 2
        assert all(w.category == "成语" for w in results)

    def test_search_category_word(self, mock_search_engine):
        """Test search for regular words."""
        results = mock_search_engine.search(category="词语")
        assert len(results) == 3
        assert all(w.category == "词语" for w in results)

    def test_search_category_no_match(self, mock_search_engine):
        """Test search for category that doesn't exist."""
        results = mock_search_engine.search(category="歇后语")
        assert len(results) == 0


class TestSearchByStructure:
    """Test search by structure pattern."""

    def test_search_structure_aabb(self, mock_search_engine):
        """Test search for AABB structure."""
        results = mock_search_engine.search(structure="AABB")
        assert len(results) == 1
        assert results[0].word == "高高兴兴"

    def test_search_structure_abac(self, mock_search_engine):
        """Test search for ABAC structure."""
        results = mock_search_engine.search(structure="ABAC")
        assert len(results) == 1
        assert results[0].word == "一心一意"

    def test_search_structure_abab(self, mock_search_engine):
        """Test search for ABAB structure."""
        results = mock_search_engine.search(structure="ABAB")
        assert len(results) == 1
        assert results[0].word == "研究研究"

    def test_search_structure_no_match(self, mock_search_engine):
        """Test search for structure that doesn't exist in data."""
        # Search for a structure not in our sample data
        results = mock_search_engine.search(structure="AAAA")
        assert len(results) == 0


class TestSearchByPinyin:
    """Test search by pinyin initials."""

    def test_search_pinyin_initials(self, mock_search_engine):
        """Test search with pinyin initials."""
        results = mock_search_engine.search(pinyin="zg")
        assert len(results) == 1
        assert results[0].word == "中国"

    def test_search_pinyin_no_match(self, mock_search_engine):
        """Test search with pinyin that doesn't exist."""
        results = mock_search_engine.search(pinyin="xy")
        assert len(results) == 0


class TestSearchByRhyme:
    """Test search by rhyme/final."""

    def test_search_rhyme_uo(self, mock_search_engine):
        """Test search by rhyme 'uo'."""
        results = mock_search_engine.search(rhyme="uo")
        assert len(results) == 1
        assert results[0].word == "中国"

    def test_search_rhyme_ing(self, mock_search_engine):
        """Test search by rhyme 'ing'."""
        results = mock_search_engine.search(rhyme="ing")
        assert len(results) == 1
        assert results[0].word == "高高兴兴"

    def test_search_rhyme_no_match(self, mock_search_engine):
        """Test search by rhyme that doesn't exist."""
        results = mock_search_engine.search(rhyme="ang")
        assert len(results) == 0


class TestSearchByRegex:
    """Test search by regular expression."""

    def test_search_regex_simple(self, mock_search_engine):
        """Test simple regex search."""
        results = mock_search_engine.search(regex=".*意")
        assert len(results) >= 1
        assert any(w.word == "一心一意" for w in results)

    def test_search_regex_start(self, mock_search_engine):
        """Test regex with start anchor."""
        results = mock_search_engine.search(regex="^中.*")
        assert len(results) == 1
        assert results[0].word == "中国"

    def test_search_regex_invalid(self, mock_search_engine):
        """Test invalid regex returns empty."""
        results = mock_search_engine.search(regex="[invalid")
        assert len(results) == 0


class TestSearchCombined:
    """Test combined search criteria."""

    def test_search_regex_and_length(self, mock_search_engine):
        """Test search with regex and length combined."""
        results = mock_search_engine.search(regex="^一", length=4)
        assert len(results) == 1
        assert results[0].word == "一心一意"

    def test_search_category_and_structure(self, mock_search_engine):
        """Test search with category and structure combined."""
        results = mock_search_engine.search(category="成语", structure="ABAC")
        assert len(results) == 1
        assert results[0].word == "一心一意"

    def test_search_regex_start_end_combined(self, mock_search_engine):
        """Test search with regex start/end combined."""
        results = mock_search_engine.search(regex="^中.*国$")
        assert len(results) == 1
        assert results[0].word == "中国"

    def test_search_multiple_filters_no_match(self, mock_search_engine):
        """Test combined search with no matching results."""
        results = mock_search_engine.search(regex="^中.*意$")
        assert len(results) == 0


class TestSearchLimit:
    """Test search limit parameter."""

    def test_search_limit_default(self, mock_search_engine):
        """Test default limit is applied."""
        results = mock_search_engine.search(length=4)
        assert len(results) <= 20

    def test_search_limit_small(self, mock_search_engine):
        """Test small limit."""
        results = mock_search_engine.search(length=4, limit=2)
        assert len(results) <= 2

    def test_search_limit_large(self, mock_search_engine):
        """Test large limit."""
        results = mock_search_engine.search(limit=100)
        assert len(results) <= len(mock_search_engine.words)


class TestSearchEdgeCases:
    """Test edge cases for search."""

    def test_search_no_criteria(self, mock_search_engine):
        """Test search with no criteria returns all words up to limit."""
        results = mock_search_engine.search()
        assert len(results) > 0
        assert len(results) <= 20

    def test_search_zero_limit(self, mock_search_engine):
        """Test search with zero limit returns all results."""
        results = mock_search_engine.search(limit=0)
        assert len(results) > 0
        assert len(results) == len(mock_search_engine.words)


class TestSearchPinyinExpansion:
    """Test pinyin expansion for regex searches."""

    def test_regex_with_pinyin_disabled(self, mock_search_engine):
        """Test regex search without pinyin expansion."""
        results = mock_search_engine.search(regex="^yi.*yi.*$", enable_pinyin=False)
        assert len(results) == 0

    def test_regex_with_pinyin_enabled(self, mock_search_engine):
        """Test regex search with pinyin expansion."""
        results = mock_search_engine.search(regex="^yi.*yi.*$", enable_pinyin=True)
        assert len(results) >= 1
        assert any(w.word == "一心一意" for w in results)

    def test_regex_pinyin_complex_pattern(self, mock_search_engine):
        """Test regex with complex pattern and pinyin expansion."""
        results = mock_search_engine.search(regex="yan.*yan", enable_pinyin=True)
        assert len(results) >= 1
        assert any(w.word == "研究研究" for w in results)

    def test_regex_multi_syllable_pinyin(self, mock_search_engine):
        """Test regex with multi-syllable pinyin (e.g., 'yixin')."""
        results = mock_search_engine.search(regex="^yixin", enable_pinyin=True)
        assert len(results) >= 1
        assert any(w.word == "一心一意" for w in results)
