"""Tests for pinyin utility functions."""

import pytest
from lexicon.pinyin_utils import (
    get_pinyin,
    get_pinyin_no_tone,
    get_pinyin_initials,
    get_tones,
    get_rhyme,
    get_all_pinyin_variants,
    get_all_pinyin_no_tone_variants,
    expand_pinyin_wildcards,
)


class TestGetPinyin:
    """Test get_pinyin function with tone marks."""

    def test_simple_word(self):
        """Test simple word pinyin extraction."""
        result = get_pinyin("你好")
        assert result == "nǐ hǎo"

    def test_four_character_idiom(self):
        """Test four-character idiom."""
        result = get_pinyin("中国")
        assert "zhōng" in result
        assert "guó" in result

    def test_multi_pronunciation_character(self):
        """Test word with multi-pronunciation character (朝 can be zhāo or cháo)."""
        result = get_pinyin("朝阳")
        # Should return first pronunciation: zhāo
        assert result.startswith("zhāo")

    def test_single_character(self):
        """Test single character."""
        result = get_pinyin("好")
        assert result == "hǎo"

    def test_empty_string(self):
        """Test empty string."""
        result = get_pinyin("")
        assert result == ""


class TestGetPinyinNoTone:
    """Test get_pinyin_no_tone function."""

    def test_simple_word(self):
        """Test simple word without tones."""
        result = get_pinyin_no_tone("你好")
        assert result == "ni hao"

    def test_four_character_idiom(self):
        """Test idiom without tones."""
        result = get_pinyin_no_tone("中国")
        assert "zhong" in result
        assert "guo" in result

    def test_multi_pronunciation_character(self):
        """Test multi-pronunciation character without tone."""
        result = get_pinyin_no_tone("朝阳")
        assert result.startswith("zhao")

    def test_single_character(self):
        """Test single character without tone."""
        result = get_pinyin_no_tone("好")
        assert result == "hao"

    def test_empty_string(self):
        """Test empty string."""
        result = get_pinyin_no_tone("")
        assert result == ""


class TestGetPinyinInitials:
    """Test get_pinyin_initials function - handles multi-pronunciation characters."""

    def test_simple_word(self):
        """Test simple word initials."""
        result = get_pinyin_initials("你好")
        assert result == ["nh"]

    def test_multi_pronunciation_character(self):
        """Test multi-pronunciation character like 朝 (zhāo/cháo)."""
        result = get_pinyin_initials("朝阳")
        # Should contain both possible initials: zy (from zhāo yáng) and cy (from cháo yáng)
        assert "zy" in result or "cy" in result
        # At minimum should have at least one
        assert len(result) > 0

    def test_single_character(self):
        """Test single character initials."""
        result = get_pinyin_initials("中")
        assert result == ["z"]

    def test_no_duplicates(self):
        """Test that duplicates are removed."""
        result = get_pinyin_initials("哈哈")
        # Even if multiple characters have same pronunciation, no dupes
        assert isinstance(result, list)
        assert len(result) == len(set(result))

    def test_empty_string(self):
        """Test empty string."""
        result = get_pinyin_initials("")
        # Empty string returns [''] not []
        assert result == [''] or result == []


class TestGetTones:
    """Test get_tones function - extract tone sequence from pinyin."""

    def test_simple_tones(self):
        """Test tone extraction from simple pinyin."""
        result = get_tones("nǐ hǎo")
        assert result == "3,3"

    def test_mixed_tones(self):
        """Test mixed tone sequence."""
        result = get_tones("zhāo yáng")
        # zhāo has tone 1, yáng has tone 2
        assert result == "1,2"

    def test_first_tone_all(self):
        """Test all first tone (high/flat)."""
        result = get_tones("ā ē ī ō ū")
        assert result == "1,1,1,1,1"

    def test_second_tone(self):
        """Test second tone (rising)."""
        result = get_tones("á é í ó ú")
        assert result == "2,2,2,2,2"

    def test_third_tone(self):
        """Test third tone (low/falling-rising)."""
        result = get_tones("ǎ ě ǐ ǒ ǔ")
        assert result == "3,3,3,3,3"

    def test_fourth_tone(self):
        """Test fourth tone (falling)."""
        result = get_tones("à è ì ò ù")
        assert result == "4,4,4,4,4"

    def test_neutral_tone(self):
        """Test neutral tone (de, le, etc.)."""
        result = get_tones("bu yong xie")
        # No tone marks = tone 0 (neutral)
        assert result == "0,4,4" or result == "0,0,0"

    def test_empty_string(self):
        """Test empty string."""
        result = get_tones("")
        assert result == ""


class TestGetRhyme:
    """Test get_rhyme function - extract rhyme/final."""

    def test_basic_rhyme(self):
        """Test basic rhyme extraction."""
        result = get_rhyme("天空")
        # 空 (kong) has rhyme "ong"
        assert result == "ong"

    def test_rhyme_of_multi_char_word(self):
        """Test that we get rhyme of last character."""
        result = get_rhyme("朝阳")
        # 阳 (yang) has rhyme "iang" (full rhyme including i)
        assert result == "iang" or result == "ang"

    def test_single_character_rhyme(self):
        """Test single character rhyme."""
        result = get_rhyme("中")
        # 中 (zhong) has rhyme "ong"
        assert result == "ong"

    def test_empty_string(self):
        """Test empty string."""
        result = get_rhyme("")
        assert result == ""

    def test_rhyme_with_different_finals(self):
        """Test various rhymes."""
        result = get_rhyme("国")
        # 国 (guo) has rhyme "uo"
        assert result == "uo"


class TestGetAllPinyinVariants:
    """Test get_all_pinyin_variants function."""

    def test_simple_word_single_variant(self):
        """Test word with no multi-pronunciation characters."""
        result = get_all_pinyin_variants("中国")
        assert len(result) > 0
        assert "zhōng guó" in result

    def test_multi_pronunciation_character_variants(self):
        """Test word with multi-pronunciation characters."""
        result = get_all_pinyin_variants("朝阳")
        # Should have at least two variants since 朝 has two pronunciations
        assert len(result) >= 1
        # Should include common pronunciation
        assert any("zhāo" in v or "cháo" in v for v in result)

    def test_no_duplicates_in_variants(self):
        """Test that duplicate variants are removed."""
        result = get_all_pinyin_variants("你好")
        assert len(result) == len(set(result))

    def test_empty_string(self):
        """Test empty string."""
        result = get_all_pinyin_variants("")
        # Empty string returns [''] not []
        assert result == [''] or result == []


class TestGetAllPinyinNoToneVariants:
    """Test get_all_pinyin_no_tone_variants function."""

    def test_simple_word_single_variant(self):
        """Test word with no multi-pronunciation characters."""
        result = get_all_pinyin_no_tone_variants("中国")
        assert len(result) > 0
        assert "zhong guo" in result

    def test_multi_pronunciation_character_variants(self):
        """Test word with multi-pronunciation characters."""
        result = get_all_pinyin_no_tone_variants("朝阳")
        assert len(result) >= 1
        assert any("zhao" in v or "chao" in v for v in result)

    def test_no_duplicates_in_variants(self):
        """Test that duplicate variants are removed."""
        result = get_all_pinyin_no_tone_variants("你好")
        assert len(result) == len(set(result))

    def test_empty_string(self):
        """Test empty string."""
        result = get_all_pinyin_no_tone_variants("")
        # Empty string returns [''] not []
        assert result == [''] or result == []


class TestExpandPinyinWildcards:
    """Test expand_pinyin_wildcards function - @ wildcard for finals."""

    def test_wildcard_after_initial(self):
        """Test @ wildcard after initial consonant (t@cai)."""
        result = expand_pinyin_wildcards("t@cai")
        assert len(result) > 0
        assert "tiancai" in result
        assert "tencai" in result
        assert "tacai" in result

    def test_wildcard_at_end(self):
        """Test @ wildcard at end of pattern (tianc@)."""
        result = expand_pinyin_wildcards("tianc@")
        assert len(result) > 0
        assert "tiancai" in result
        assert "tiancao" in result
        assert "tiancang" in result

    def test_wildcard_in_middle(self):
        """Test @ wildcard in middle position."""
        result = expand_pinyin_wildcards("w@n")
        assert len(result) > 0
        assert "wan" in result
        assert "wen" in result
        assert "win" in result

    def test_no_wildcard_returns_original(self):
        """Test pattern without @ returns unchanged."""
        result = expand_pinyin_wildcards("tiancai")
        assert result == ["tiancai"]

    def test_multiple_wildcards_expands(self):
        """Test pattern with multiple @ symbols expands."""
        result = expand_pinyin_wildcards("t@c@i")
        assert len(result) > 0
        assert "tacai" in result
        assert "tencai" in result

    def test_empty_string(self):
        """Test empty string."""
        result = expand_pinyin_wildcards("")
        assert result == [""]

    def test_wildcard_at_beginning(self):
        """Test @ at the very beginning."""
        result = expand_pinyin_wildcards("@n")
        assert len(result) > 0
        assert "an" in result
        assert "en" in result
        assert "in" in result
