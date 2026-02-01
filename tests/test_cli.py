"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner
from lexicon.cli import app
from lexicon.models import Word
from lexicon.search import SearchEngine
from lexicon.index import LexiconIndex
from unittest.mock import Mock, patch
import random


runner = CliRunner()


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
            structure=None,
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
    ]


@pytest.fixture
def sample_words_for_fill():
    """Create sample words for fill command testing with multiple matches."""
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
            structure=None,
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
            word="天下地厚",
            pinyin="tiān xià dì hòu",
            pinyin_no_tone="tian xia di hou",
            pinyin_initials="txdh",
            tones="1,4,4,4",
            rhyme="ou",
            first_char="天",
            last_char="厚",
            chars=["天", "下", "地", "厚"],
            length=4,
            definition="比喻天地恩德",
            source=None,
            example=None,
            category="成语",
            structure=None,
            synonyms=None,
            antonyms=None,
            frequency=None,
        ),
        Word(
            word="天地一家",
            pinyin="tiān dì yī jiā",
            pinyin_no_tone="tian di yi jia",
            pinyin_initials="tdyj",
            tones="1,4,1,1",
            rhyme="ia",
            first_char="天",
            last_char="家",
            chars=["天", "地", "一", "家"],
            length=4,
            definition="天地人合一",
            source=None,
            example=None,
            category="成语",
            structure=None,
            synonyms=None,
            antonyms=None,
            frequency=None,
        ),
    ]


@pytest.fixture
def mock_search_engine(sample_words):
    """Create mock SearchEngine."""
    engine = SearchEngine.__new__(SearchEngine)
    engine.words = sample_words
    engine.index = LexiconIndex(sample_words)
    return engine


class TestSearchCommand:
    """Test search command."""

    def test_search_help(self):
        """Test search command help."""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "首字" in result.stdout or "--start" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_no_criteria(self, mock_get_engine, mock_search_engine):
        """Test search with no criteria."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search"])
        assert result.exit_code == 0
        assert "找到" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_by_start(self, mock_get_engine, mock_search_engine):
        """Test search by start character."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--start", "中"])
        assert result.exit_code == 0
        assert "中国" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_by_end(self, mock_get_engine, mock_search_engine):
        """Test search by end character."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--end", "国"])
        assert result.exit_code == 0
        assert "中国" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_by_length(self, mock_get_engine, mock_search_engine):
        """Test search by length."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--length", "2"])
        assert result.exit_code == 0
        assert "中国" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_by_category(self, mock_get_engine, mock_search_engine):
        """Test search by category."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--category", "成语"])
        assert result.exit_code == 0
        assert "天长地久" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_with_limit(self, mock_get_engine, mock_search_engine):
        """Test search with limit."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--limit", "1"])
        assert result.exit_code == 0
        assert "找到" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_invalid_limit(self, mock_get_engine, mock_search_engine):
        """Test search with invalid limit."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--limit", "-1"])
        assert result.exit_code == 1

    @patch("lexicon.cli.get_search_engine")
    def test_search_no_results(self, mock_get_engine, mock_search_engine):
        """Test search with no results."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--start", "金"])
        assert result.exit_code == 0
        assert "未找到" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_no_pinyin_flag(self, mock_get_engine, mock_search_engine):
        """Test search with --no-pinyin flag."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--start", "中", "--no-pinyin"])
        assert result.exit_code == 0
        assert "中国" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_search_no_definition_flag(self, mock_get_engine, mock_search_engine):
        """Test search with --no-definition flag."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["search", "--start", "中", "--no-definition"])
        assert result.exit_code == 0
        assert "中国" in result.stdout


class TestDefineCommand:
    """Test define command."""

    def test_define_help(self):
        """Test define command help."""
        result = runner.invoke(app, ["define", "--help"])
        assert result.exit_code == 0

    @patch("lexicon.cli.get_search_engine")
    def test_define_existing_word(self, mock_get_engine, mock_search_engine):
        """Test define for existing word."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["define", "中国"])
        assert result.exit_code == 0
        assert "📖" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_define_nonexistent_word(self, mock_get_engine, mock_search_engine):
        """Test define for non-existent word."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["define", "不存在"])
        # Should exit gracefully with 0 (just no results)
        assert "不存在" in result.stdout or "词语" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_define_empty_word(self, mock_get_engine, mock_search_engine):
        """Test define with empty word."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["define", ""])
        assert result.exit_code == 1


class TestChainCommand:
    """Test chain command."""

    def test_chain_help(self):
        """Test chain command help."""
        result = runner.invoke(app, ["chain", "--help"])
        assert result.exit_code == 0

    @patch("lexicon.cli.get_search_engine")
    def test_chain_basic(self, mock_get_engine, mock_search_engine):
        """Test basic chain command."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["chain", "中", "--count", "2"])
        assert result.exit_code == 0 or result.exit_code == 1
        # Should have chain output or error message
        assert "🔗" in result.stdout or "无法找到" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_chain_invalid_char(self, mock_get_engine, mock_search_engine):
        """Test chain with invalid char length."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["chain", "中国"])
        assert result.exit_code == 1

    @patch("lexicon.cli.get_search_engine")
    def test_chain_invalid_count(self, mock_get_engine, mock_search_engine):
        """Test chain with invalid count."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["chain", "中", "--count", "0"])
        assert result.exit_code == 1


class TestRandomWordCommand:
    """Test random-word command."""

    def test_random_word_help(self):
        """Test random-word command help."""
        result = runner.invoke(app, ["random-word", "--help"])
        assert result.exit_code == 0

    @patch("lexicon.cli.get_search_engine")
    def test_random_word_basic(self, mock_get_engine, mock_search_engine):
        """Test basic random-word command."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["random-word"])
        assert result.exit_code == 0
        assert "🎲" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_random_word_by_length(self, mock_get_engine, mock_search_engine):
        """Test random-word with length filter."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["random-word", "--length", "2"])
        assert result.exit_code == 0
        assert "🎲" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_random_word_by_category(self, mock_get_engine, mock_search_engine):
        """Test random-word with category filter."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["random-word", "--category", "成语"])
        assert result.exit_code == 0
        assert "🎲" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_random_word_invalid_length(self, mock_get_engine, mock_search_engine):
        """Test random-word with invalid length."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["random-word", "--length", "0"])
        assert result.exit_code == 1


class TestStatsCommand:
    """Test stats command."""

    def test_stats_help(self):
        """Test stats command help."""
        result = runner.invoke(app, ["stats", "--help"])
        assert result.exit_code == 0

    @patch("lexicon.cli.get_search_engine")
    def test_stats_basic(self, mock_get_engine, mock_search_engine):
        """Test basic stats command."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "📊" in result.stdout


class TestFreqCommand:
    """Test freq command."""

    def test_freq_help(self):
        """Test freq command help."""
        result = runner.invoke(app, ["freq", "--help"])
        assert result.exit_code == 0

    @patch("lexicon.cli.get_search_engine")
    def test_freq_all(self, mock_get_engine, mock_search_engine):
        """Test freq command with all position."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["freq", "--position", "all"])
        assert result.exit_code == 0
        assert "📊" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_freq_start(self, mock_get_engine, mock_search_engine):
        """Test freq command with start position."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["freq", "--position", "start"])
        assert result.exit_code == 0
        assert "📊" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_freq_end(self, mock_get_engine, mock_search_engine):
        """Test freq command with end position."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["freq", "--position", "end"])
        assert result.exit_code == 0
        assert "📊" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_freq_invalid_position(self, mock_get_engine, mock_search_engine):
        """Test freq command with invalid position."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["freq", "--position", "invalid"])
        assert result.exit_code == 1

    @patch("lexicon.cli.get_search_engine")
    def test_freq_invalid_limit(self, mock_get_engine, mock_search_engine):
        """Test freq command with invalid limit."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["freq", "--limit", "-1"])
        assert result.exit_code == 1


class TestQuizCommand:
    """Test quiz command."""

    @patch("random.choice")
    @patch("lexicon.cli.get_search_engine")
    def test_quiz_correct_guess_first_attempt(self, mock_get_engine, mock_choice, mock_search_engine):
        """Test quiz with correct guess on first attempt."""
        quiz_runner = CliRunner()
        mock_get_engine.return_value = mock_search_engine
        mock_choice.side_effect = lambda x: x[0]  # Always select first word
        result = quiz_runner.invoke(app, ["quiz"], input="中国\n")
        assert result.exit_code == 0
        assert "🎯" in result.stdout
        assert "✅ 正确" in result.stdout

    @patch("random.choice")
    @patch("lexicon.cli.get_search_engine")
    def test_quiz_with_category_filter(self, mock_get_engine, mock_choice, mock_search_engine):
        """Test quiz with category filter."""
        quiz_runner = CliRunner()
        mock_get_engine.return_value = mock_search_engine
        # The second word (index 1) is "天长地久" which matches the category "成语"
        mock_choice.side_effect = lambda x: x[1] if len(x) > 1 else x[0]
        result = quiz_runner.invoke(app, ["quiz", "--category", "成语"], input="天长地久\n")
        assert result.exit_code == 0
        assert "🎯" in result.stdout

    @patch("random.choice")
    @patch("lexicon.cli.get_search_engine")
    def test_quiz_with_length_filter(self, mock_get_engine, mock_choice, mock_search_engine):
        """Test quiz with length filter."""
        quiz_runner = CliRunner()
        mock_get_engine.return_value = mock_search_engine
        mock_choice.side_effect = lambda x: x[0]  # Always select first word
        result = quiz_runner.invoke(app, ["quiz", "--length", "2"], input="中国\n")
        assert result.exit_code == 0
        assert "🎯" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_quiz_invalid_length(self, mock_get_engine, mock_search_engine):
        """Test quiz with invalid length."""
        quiz_runner = CliRunner()
        mock_get_engine.return_value = mock_search_engine
        result = quiz_runner.invoke(app, ["quiz", "--length", "0"])
        assert result.exit_code == 1

    @patch("lexicon.cli.get_search_engine")
    def test_quiz_no_matching_words(self, mock_get_engine, mock_search_engine):
        """Test quiz with no matching words."""
        quiz_runner = CliRunner()
        mock_get_engine.return_value = mock_search_engine
        result = quiz_runner.invoke(app, ["quiz", "--length", "100"])
        assert result.exit_code == 1
        assert "未找到" in result.stdout


@pytest.fixture
def mock_search_engine_for_fill(sample_words_for_fill):
    """Create mock SearchEngine for fill tests."""
    engine = SearchEngine.__new__(SearchEngine)
    engine.words = sample_words_for_fill
    engine.index = LexiconIndex(sample_words_for_fill)
    return engine


class TestFillCommand:
    """Test fill command."""

    def test_fill_help(self):
        """Test fill command help."""
        result = runner.invoke(app, ["fill", "--help"])
        assert result.exit_code == 0

    @patch("lexicon.cli.get_search_engine")
    def test_fill_no_pattern(self, mock_get_engine, mock_search_engine):
        """Test fill without pattern."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["fill", ""])
        assert result.exit_code == 1

    @patch("lexicon.cli.get_search_engine")
    def test_fill_pattern_without_question_mark(self, mock_get_engine, mock_search_engine):
        """Test fill with pattern without question mark."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["fill", "中国"])
        assert result.exit_code == 1
        assert "?" in result.stderr or "?" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_fill_no_matches(self, mock_get_engine, mock_search_engine_for_fill):
        """Test fill with no matches."""
        mock_get_engine.return_value = mock_search_engine_for_fill
        result = runner.invoke(app, ["fill", "金?金?"])
        assert result.exit_code == 0
        assert "未找到" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_fill_one_match(self, mock_get_engine, mock_search_engine):
        """Test fill with exactly one match."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["fill", "中?"])
        assert result.exit_code == 0
        assert "✨" in result.stdout or "中国" in result.stdout

    @patch("random.choice")
    @patch("lexicon.cli.get_search_engine")
    def test_fill_multiple_matches_game_mode(self, mock_get_engine, mock_choice, mock_search_engine_for_fill):
        """Test fill with 2-10 matches triggers game mode."""
        mock_get_engine.return_value = mock_search_engine_for_fill
        mock_choice.side_effect = lambda x: x[0]
        result = runner.invoke(app, ["fill", "天?地?"], input="天长地久\n")
        assert result.exit_code == 0
        assert "🎯" in result.stdout or "✅" in result.stdout

    @patch("lexicon.cli.get_search_engine")
    def test_fill_invalid_limit(self, mock_get_engine, mock_search_engine):
        """Test fill with invalid limit."""
        mock_get_engine.return_value = mock_search_engine
        result = runner.invoke(app, ["fill", "一?一?", "--limit", "-1"])
        assert result.exit_code == 1

    @patch("lexicon.cli.get_search_engine")
    def test_fill_with_category_filter(self, mock_get_engine, mock_search_engine_for_fill):
        """Test fill with category filter."""
        mock_get_engine.return_value = mock_search_engine_for_fill
        result = runner.invoke(app, ["fill", "天?地?", "--category", "成语"])
        assert result.exit_code == 0 or "天" in result.stdout

    @patch("random.choice")
    @patch("lexicon.cli.get_search_engine")
    def test_fill_game_correct_guess(self, mock_get_engine, mock_choice, mock_search_engine_for_fill):
        """Test fill game with correct guess."""
        mock_get_engine.return_value = mock_search_engine_for_fill
        mock_choice.side_effect = lambda x: x[0]
        result = runner.invoke(app, ["fill", "天?地?"], input="天长地久\n")
        assert result.exit_code == 0
        assert "✅" in result.stdout

    @patch("random.choice")
    @patch("lexicon.cli.get_search_engine")
    def test_fill_game_wrong_guess_then_correct(self, mock_get_engine, mock_choice, mock_search_engine_for_fill):
        """Test fill game with wrong then correct guess."""
        mock_get_engine.return_value = mock_search_engine_for_fill
        mock_choice.side_effect = lambda x: x[0]
        result = runner.invoke(app, ["fill", "天?地?"], input="错误答案\n天长地久\n")
        assert result.exit_code == 0
        assert "✅" in result.stdout


class TestCliIntegration:
    """Integration tests for CLI."""

    def test_app_help(self):
        """Test main app help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Lexicon-Lab" in result.stdout or "help" in result.stdout.lower()

    @patch("lexicon.cli.get_search_engine")
    def test_get_search_engine_error(self, mock_get_engine):
        """Test handling of search engine initialization error."""
        mock_get_engine.side_effect = Exception("Test error")
        result = runner.invoke(app, ["search"])
        assert result.exit_code == 1
