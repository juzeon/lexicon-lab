"""Search engine for Chinese words with data loading and conversion."""

import hashlib
import logging
import pickle
import re
from pathlib import Path
from typing import List

import orjson
from pypinyin import lazy_pinyin, Style

from lexicon.models import Word
from lexicon.index import LexiconIndex
from lexicon.pinyin_utils import (
    get_pinyin,
    get_pinyin_no_tone,
    get_pinyin_initials,
    get_tones,
    get_rhyme,
)
from lexicon.structure import detect_structure

# Set up logger
logger = logging.getLogger(__name__)


class SearchEngine:
    """Search engine that loads and searches Chinese words from JSON files."""

    CACHE_DIR = Path.home() / ".cache" / "lexicon-lab"
    CACHE_FILE = CACHE_DIR / "index.pkl"

    def __init__(self, data_dir: str = "data/raw"):
        """Initialize SearchEngine and load all data.
        
        Uses pickle caching for faster startup. Cache is validated with MD5 hash
        of data files and auto-invalidates when data changes.
        
        Args:
            data_dir: Directory containing JSON data files (default: "data/raw")
        """
        self.data_dir = Path(data_dir)
        self.words: List[Word] = []

        # Try to load from cache first
        if self._load_from_cache():
            logger.info("Loaded from cache successfully")
        else:
            logger.info("Loading from JSON files...")
            self._load_data()

            logger.info("Building lexicon index...")
            self.index = LexiconIndex(self.words)
            logger.info("Index built successfully")

            # Save to cache for next time
            self._save_to_cache()

    def _calculate_data_hash(self) -> str:
        """Calculate MD5 hash of all data files.
        
        Returns:
            MD5 hash string of combined data files
        """
        hash_md5 = hashlib.md5()

        for filename in ["idiom.json", "word.json", "xiehouyu.json", "ci.json"]:
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    hash_md5.update(f.read())

        return hash_md5.hexdigest()

    def _load_from_cache(self) -> bool:
        """Try to load words and index from pickle cache.
        
        Returns:
            True if cache was loaded successfully, False otherwise
        """
        if not self.CACHE_FILE.exists():
            logger.debug(f"Cache file not found: {self.CACHE_FILE}")
            return False

        try:
            current_hash = self._calculate_data_hash()

            with open(self.CACHE_FILE, 'rb') as f:
                cache_data = pickle.load(f)

            cached_hash = cache_data.get('data_hash')
            if cached_hash != current_hash:
                logger.info("Cache invalidated: data files have changed")
                return False

            self.words = cache_data.get('words', [])
            self.index = cache_data.get('index')

            logger.info(f"Cache hit: loaded {len(self.words)} words from cache")
            return True

        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}. Falling back to JSON loading.")
            return False

    def _save_to_cache(self) -> None:
        """Save words and index to pickle cache.
        
        Creates cache directory if it doesn't exist.
        Gracefully handles cache saving failures.
        """
        try:
            # Create cache directory if it doesn't exist
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

            data_hash = self._calculate_data_hash()
            cache_data = {
                'data_hash': data_hash,
                'words': self.words,
                'index': self.index,
            }

            with open(self.CACHE_FILE, 'wb') as f:
                pickle.dump(cache_data, f)

            logger.debug(f"Saved cache to {self.CACHE_FILE}")

        except Exception as e:
            logger.warning(f"Failed to save cache: {e}. Continuing without cache.")

    def _load_data(self) -> None:
        """Load all JSON data files and convert to Word objects."""
        # Load idioms (成语)
        idiom_file = self.data_dir / "idiom.json"
        if idiom_file.exists():
            logger.info("Loading idioms...")
            self._load_idioms(idiom_file)
            logger.info(f"Loaded {len([w for w in self.words if w.category == '成语'])} idioms")
        else:
            logger.warning(f"Idiom file not found: {idiom_file}")

        # Load words (词语)
        word_file = self.data_dir / "word.json"
        if word_file.exists():
            logger.info("Loading words...")
            before_count = len(self.words)
            self._load_words(word_file)
            logger.info(f"Loaded {len(self.words) - before_count} words")
        else:
            logger.warning(f"Word file not found: {word_file}")

        # Load xiehouyu (歇后语)
        xiehouyu_file = self.data_dir / "xiehouyu.json"
        if xiehouyu_file.exists():
            logger.info("Loading xiehouyu...")
            before_count = len(self.words)
            self._load_xiehouyu(xiehouyu_file)
            logger.info(f"Loaded {len(self.words) - before_count} xiehouyu")
        else:
            logger.warning(f"Xiehouyu file not found: {xiehouyu_file}")

        # Load ci (词语 from ci.json)
        ci_file = self.data_dir / "ci.json"
        if ci_file.exists():
            logger.info("Loading ci...")
            before_count = len(self.words)
            self._load_ci(ci_file)
            logger.info(f"Loaded {len(self.words) - before_count} ci")
        else:
            logger.warning(f"Ci file not found: {ci_file}")

        logger.info(f"Total words loaded: {len(self.words)}")

    def _load_idioms(self, filepath: Path) -> None:
        """Load idioms from JSON file.
        
        Idiom JSON format:
        {
            "word": "阿鼻地狱",
            "pinyin": "ā bí dì yù",
            "explanation": "...",
            "derivation": "...",
            "example": "...",
            "abbreviation": "abdy"
        }
        """
        with open(filepath, 'rb') as f:
            data = orjson.loads(f.read())

        for entry in data:
            try:
                word_text = entry.get("word", "").strip()
                if not word_text:
                    continue

                # Generate pinyin data
                pinyin_with_tone = get_pinyin(word_text)
                pinyin_no_tone = get_pinyin_no_tone(word_text)
                pinyin_initials = get_pinyin_initials(word_text)
                tones = get_tones(pinyin_with_tone)
                rhyme = get_rhyme(word_text)

                # Extract character information
                chars = list(word_text)
                first_char = chars[0] if chars else ""
                last_char = chars[-1] if chars else ""
                length = len(chars)

                # Get definition and other fields
                definition = entry.get("explanation", "").strip()
                definition = " ".join(definition.split())
                source = entry.get("derivation", "").strip() or None
                example = entry.get("example", "").strip() or None

                # Detect structure pattern
                structure = detect_structure(word_text)

                # Create Word object
                word = Word(
                    word=word_text,
                    pinyin=pinyin_with_tone,
                    pinyin_no_tone=pinyin_no_tone,
                    pinyin_initials=pinyin_initials[0] if pinyin_initials else "",
                    tones=tones,
                    rhyme=rhyme,
                    first_char=first_char,
                    last_char=last_char,
                    chars=chars,
                    length=length,
                    definition=definition,
                    source=source,
                    example=example,
                    category="成语",
                    structure=structure,
                    synonyms=None,
                    antonyms=None,
                    frequency=None,
                )

                self.words.append(word)

            except Exception as e:
                logger.warning(f"Failed to process idiom entry {entry.get('word', '?')}: {e}")
                continue

    def _load_words(self, filepath: Path) -> None:
        """Load regular words from JSON file.
        
        Word JSON format:
        {
            "word": "嗄",
            "oldword": "嗄",
            "strokes": "13",
            "pinyin": "á",
            "radicals": "口",
            "explanation": "...",
            "more": "..."
        }
        """
        with open(filepath, 'rb') as f:
            data = orjson.loads(f.read())

        for entry in data:
            try:
                word_text = entry.get("word", "").strip()
                if not word_text:
                    continue

                # Generate pinyin data
                pinyin_with_tone = get_pinyin(word_text)
                pinyin_no_tone = get_pinyin_no_tone(word_text)
                pinyin_initials = get_pinyin_initials(word_text)
                tones = get_tones(pinyin_with_tone)
                rhyme = get_rhyme(word_text)

                # Extract character information
                chars = list(word_text)
                first_char = chars[0] if chars else ""
                last_char = chars[-1] if chars else ""
                length = len(chars)

                # Get definition (use explanation field)
                definition = entry.get("explanation", "").strip()
                if not definition:
                    definition = entry.get("more", "").strip()
                definition = " ".join(definition.split())

                # Detect structure pattern
                structure = detect_structure(word_text)

                # Create Word object
                word = Word(
                    word=word_text,
                    pinyin=pinyin_with_tone,
                    pinyin_no_tone=pinyin_no_tone,
                    pinyin_initials=pinyin_initials[0] if pinyin_initials else "",
                    tones=tones,
                    rhyme=rhyme,
                    first_char=first_char,
                    last_char=last_char,
                    chars=chars,
                    length=length,
                    definition=definition,
                    source=None,  # Words don't have source field
                    example=None,  # Words don't have example field
                    category="词语",
                    structure=structure,
                    synonyms=None,
                    antonyms=None,
                    frequency=None,
                )

                self.words.append(word)

            except Exception as e:
                logger.warning(f"Failed to process word entry {entry.get('word', '?')}: {e}")
                continue

    def _load_xiehouyu(self, filepath: Path) -> None:
        """Load xiehouyu (歇后语) from JSON file.
        
        Xiehouyu JSON format:
        {
            "riddle": "做砖的坯子、插刀的鞘子",
            "answer": "框框套套"
        }
        """
        with open(filepath, 'rb') as f:
            data = orjson.loads(f.read())

        for entry in data:
            try:
                riddle = entry.get("riddle", "").strip()
                answer = entry.get("answer", "").strip()

                if not riddle or not answer:
                    continue

                # Use the riddle as the word
                word_text = riddle

                # Generate pinyin data
                pinyin_with_tone = get_pinyin(word_text)
                pinyin_no_tone = get_pinyin_no_tone(word_text)
                pinyin_initials = get_pinyin_initials(word_text)
                tones = get_tones(pinyin_with_tone)
                rhyme = get_rhyme(word_text)

                # Extract character information
                chars = list(word_text)
                first_char = chars[0] if chars else ""
                last_char = chars[-1] if chars else ""
                length = len(chars)

                # Use answer as definition
                definition = answer
                definition = " ".join(definition.split())

                # Detect structure pattern
                structure = detect_structure(word_text)

                # Create Word object
                word = Word(
                    word=word_text,
                    pinyin=pinyin_with_tone,
                    pinyin_no_tone=pinyin_no_tone,
                    pinyin_initials=pinyin_initials[0] if pinyin_initials else "",
                    tones=tones,
                    rhyme=rhyme,
                    first_char=first_char,
                    last_char=last_char,
                    chars=chars,
                    length=length,
                    definition=definition,
                    source=None,
                    example=None,
                    category="歇后语",
                    structure=structure,
                    synonyms=None,
                    antonyms=None,
                    frequency=None,
                )

                self.words.append(word)

            except Exception as e:
                logger.warning(f"Failed to process xiehouyu entry {entry.get('riddle', '?')}: {e}")
                continue

    def _load_ci(self, filepath: Path) -> None:
        """Load ci (词语) from JSON file.
        
        Ci JSON format:
        {
            "ci": "词语",
            "explanation": "释义"
        }
        """
        with open(filepath, 'rb') as f:
            data = orjson.loads(f.read())

        for entry in data:
            try:
                word_text = entry.get("ci", "").strip()
                if not word_text:
                    continue

                pinyin_with_tone = get_pinyin(word_text)
                pinyin_no_tone = get_pinyin_no_tone(word_text)
                pinyin_initials = get_pinyin_initials(word_text)
                tones = get_tones(pinyin_with_tone)
                rhyme = get_rhyme(word_text)

                chars = list(word_text)
                first_char = chars[0] if chars else ""
                last_char = chars[-1] if chars else ""
                length = len(chars)

                definition = entry.get("explanation", "").strip()
                definition = " ".join(definition.split())

                structure = detect_structure(word_text)

                word = Word(
                    word=word_text,
                    pinyin=pinyin_with_tone,
                    pinyin_no_tone=pinyin_no_tone,
                    pinyin_initials=pinyin_initials[0] if pinyin_initials else "",
                    tones=tones,
                    rhyme=rhyme,
                    first_char=first_char,
                    last_char=last_char,
                    chars=chars,
                    length=length,
                    definition=definition,
                    source=None,
                    example=None,
                    category="词语",
                    structure=structure,
                    synonyms=None,
                    antonyms=None,
                    frequency=None,
                )

                self.words.append(word)

            except Exception as e:
                logger.warning(f"Failed to process ci entry {entry.get('ci', '?')}: {e}")
                continue

    def search(
        self,
        pinyin: str | None = None,
        regex: str | None = None,
        length: int | None = None,
        category: str | None = None,
        structure: str | None = None,
        rhyme: str | None = None,
        tone: str | None = None,
        enable_pinyin: bool = False,
        enable_homophone: bool = False,
        limit: int = 20,
        page: int = 1
    ) -> list[Word]:
        """Search for words matching the given criteria.
        
        Args:
            pinyin: Pinyin initials to match (e.g., "zgcd" for "中国成都")
            regex: Regular expression pattern to match against word text
            length: Number of characters in the word
            category: Word category (成语/词语/歇后语)
            structure: Structure pattern (e.g., "AABB", "ABAC")
            rhyme: Rhyme/final to match (e.g., "ang", "ong")
            tone: Tone sequence to match (e.g., "1,2,3,4")
            enable_pinyin: If True, expand regex searches to include all characters with matching pinyin
            enable_homophone: If True, expand pinyin searches to include similar-sounding pinyin
            limit: Results per page (0 = unlimited, default: 20)
            page: Page number (1-indexed, default: 1)
        
        Returns:
            List of Word objects matching all criteria, paginated according to limit and page
        """
        candidates = set(range(len(self.words)))

        if category is not None:
            category_indices = set(self.index.by_category.get(category, []))
            candidates &= category_indices
            if not candidates:
                return []

        if length is not None:
            length_indices = set(self.index.by_length.get(length, []))
            candidates &= length_indices
            if not candidates:
                return []

        if pinyin is not None:
            from lexicon.pinyin_utils import expand_pinyin_wildcards

            if '@' in pinyin:
                expanded_pinyins = expand_pinyin_wildcards(pinyin)
                pinyin_indices = set()
                for expanded in expanded_pinyins:
                    syllables = self._split_pinyin_syllables(expanded)
                    expanded_initials = ''.join([s[0] if s else '' for s in syllables])

                    if enable_homophone:
                        variants = self._expand_with_homophone(expanded_initials)
                        for variant in variants:
                            pinyin_indices.update(self.index.by_pinyin_initials.get(variant, []))
                    else:
                        pinyin_indices.update(self.index.by_pinyin_initials.get(expanded_initials, []))
            elif enable_homophone:
                pinyin_variants = self._expand_with_homophone(pinyin)
                pinyin_indices = set()
                for variant in pinyin_variants:
                    pinyin_indices.update(self.index.by_pinyin_initials.get(variant, []))
            else:
                pinyin_indices = set(self.index.by_pinyin_initials.get(pinyin, []))
            candidates &= pinyin_indices
            if not candidates:
                return []

        if structure is not None:
            structure_indices = set(self.index.by_structure.get(structure, []))
            candidates &= structure_indices
            if not candidates:
                return []

        if rhyme is not None:
            rhyme_indices = set(self.index.by_rhyme.get(rhyme, []))
            candidates &= rhyme_indices
            if not candidates:
                return []

        if tone is not None:
            tone_matches = []
            for idx in candidates:
                word = self.words[idx]
                if word.tones == tone:
                    tone_matches.append(idx)
            candidates = set(tone_matches)
            if not candidates:
                return []

        if regex is not None:
            try:
                if enable_pinyin:
                    pinyin_pattern = self._convert_to_pinyin_pattern(regex, enable_homophone)
                    pinyin_regex = re.compile(pinyin_pattern, re.IGNORECASE)
                    hanzi_regex = re.compile(regex)
                    
                    regex_matches = []
                    for idx in candidates:
                        word = self.words[idx]
                        pinyin_text = word.pinyin_no_tone.replace(' ', '')
                        if pinyin_regex.search(pinyin_text) or hanzi_regex.search(word.word):
                            regex_matches.append(idx)
                else:
                    expanded_regex = regex
                    regex_compiled = re.compile(expanded_regex)
                    regex_matches = []
                    for idx in candidates:
                        word = self.words[idx]
                        if regex_compiled.search(word.word):
                            regex_matches.append(idx)
                            
                candidates = set(regex_matches)
                if not candidates:
                    return []
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{regex}': {e}")
                return []

        result_indices = list(candidates)

        if limit == 0:
            return [self.words[idx] for idx in result_indices]

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_indices = result_indices[start_idx:end_idx]

        return [self.words[idx] for idx in paginated_indices]

    def _convert_to_pinyin_pattern(self, regex_pattern: str, enable_homophone: bool = False) -> str:
        from lexicon.pinyin_utils import expand_pinyin_wildcards, get_similar_pinyin
        
        if '@' in regex_pattern:
            expanded_patterns = expand_pinyin_wildcards(regex_pattern)
            if len(expanded_patterns) > 1:
                alternative_patterns = []
                for pattern in expanded_patterns:
                    converted = self._convert_to_pinyin_pattern_internal(pattern, enable_homophone)
                    alternative_patterns.append(f"(?:{converted})")
                return '|'.join(alternative_patterns)
            else:
                regex_pattern = expanded_patterns[0]
        
        return self._convert_to_pinyin_pattern_internal(regex_pattern, enable_homophone)
    
    def _convert_to_pinyin_pattern_internal(self, regex_pattern: str, enable_homophone: bool = False) -> str:
        import re as regex_module
        from lexicon.pinyin_utils import get_similar_pinyin
        
        result_parts = []
        i = 0
        in_bracket = False
        bracket_content = []
        accumulated_pinyin = ""
        
        def flush_pinyin():
            nonlocal accumulated_pinyin
            if accumulated_pinyin:
                if enable_homophone:
                    similar_pinyins = get_similar_pinyin(accumulated_pinyin)
                    all_variants = [accumulated_pinyin] + similar_pinyins
                    if len(all_variants) > 1:
                        result_parts.append(f"({'|'.join(all_variants)})")
                    else:
                        result_parts.append(accumulated_pinyin)
                else:
                    result_parts.append(accumulated_pinyin)
                accumulated_pinyin = ""
        
        while i < len(regex_pattern):
            char = regex_pattern[i]
            
            if char == '[' and (i == 0 or regex_pattern[i-1] != '\\'):
                flush_pinyin()
                in_bracket = True
                bracket_content = [char]
                i += 1
            elif char == ']' and in_bracket and (i == 0 or regex_pattern[i-1] != '\\'):
                in_bracket = False
                bracket_content.append(char)
                result_parts.append(''.join(bracket_content))
                bracket_content = []
                i += 1
            elif in_bracket:
                bracket_content.append(char)
                i += 1
            elif char == '\\' and i + 1 < len(regex_pattern):
                flush_pinyin()
                result_parts.append(char + regex_pattern[i + 1])
                i += 2
            elif char in '.^$*+?{}()|':
                flush_pinyin()
                result_parts.append(char)
                i += 1
            elif ord(char) > 127:
                flush_pinyin()
                char_pinyin = lazy_pinyin(char, style=Style.NORMAL)
                if char_pinyin:
                    result_parts.append(char_pinyin[0])
                i += 1
            else:
                accumulated_pinyin += char
                i += 1
        
        flush_pinyin()
        
        return ''.join(result_parts)

    def _expand_with_pinyin(self, text: str) -> set[str]:
        if not text or len(text) > 10:
            return {text}

        if len(text) == 1 and ord(text) > 127:
            return {text}

        result = {text}

        if text.lower() in self.index.by_char_pinyin:
            chars = self.index.by_char_pinyin[text.lower()]
            result.update(chars)

        return result

    def _split_pinyin_syllables(self, pinyin_text: str) -> list[str]:
        if not pinyin_text or not pinyin_text.isalpha():
            return [pinyin_text]

        pinyin_lower = pinyin_text.lower()

        if pinyin_lower in self.index.by_char_pinyin:
            return [pinyin_lower]

        syllables = []
        i = 0

        while i < len(pinyin_lower):
            best_match = None
            best_length = 0

            for length in range(min(6, len(pinyin_lower) - i), 0, -1):
                candidate = pinyin_lower[i:i+length]
                if candidate in self.index.by_char_pinyin:
                    if length > best_length:
                        best_match = candidate
                        best_length = length

            if best_match:
                syllables.append(best_match)
                i += best_length
            else:
                syllables.append(pinyin_lower[i])
                i += 1

        return syllables

    def _expand_pattern_with_pinyin(self, pattern: str, enable_homophone: bool = False) -> str:
        import re as regex_module

        result_parts = []
        i = 0
        accumulated_pinyin = ""

        def flush_pinyin():
            nonlocal accumulated_pinyin
            if accumulated_pinyin:
                syllables = self._split_pinyin_syllables(accumulated_pinyin)

                if enable_homophone:
                    from lexicon.pinyin_utils import get_similar_pinyin

                    for syllable in syllables:
                        syllable_chars = set()

                        base_chars = self._expand_with_pinyin(syllable)
                        syllable_chars.update(base_chars)

                        similar_pinyins = get_similar_pinyin(syllable)
                        for similar in similar_pinyins:
                            similar_chars = self._expand_with_pinyin(similar)
                            syllable_chars.update(similar_chars)

                        syllable_chars.discard(syllable)

                        if len(syllable_chars) > 1:
                            escaped_chars = [regex_module.escape(c) for c in syllable_chars]
                            result_parts.append(f"[{''.join(escaped_chars)}]")
                        elif len(syllable_chars) == 1:
                            result_parts.append(regex_module.escape(list(syllable_chars)[0]))
                        else:
                            result_parts.append(regex_module.escape(syllable))
                else:
                    for syllable in syllables:
                        expanded = self._expand_with_pinyin(syllable)
                        if len(expanded) > 1:
                            escaped_chars = [regex_module.escape(c) for c in expanded]
                            result_parts.append(f"[{''.join(escaped_chars)}]")
                        else:
                            result_parts.append(regex_module.escape(syllable))

                accumulated_pinyin = ""

        while i < len(pattern):
            char = pattern[i]

            if char == '?':
                flush_pinyin()
                result_parts.append('.')
                i += 1
            elif char == '*':
                flush_pinyin()
                result_parts.append('.*')
                i += 1
            elif char == '\\' and i + 1 < len(pattern):
                flush_pinyin()
                result_parts.append(regex_module.escape(char + pattern[i + 1]))
                i += 2
            elif ord(char) > 127:
                flush_pinyin()
                result_parts.append(regex_module.escape(char))
                i += 1
            else:
                accumulated_pinyin += char
                i += 1

        flush_pinyin()

        return ''.join(result_parts)

    def _expand_regex_with_pinyin(self, regex_pattern: str, enable_homophone: bool = False) -> str:
        import re as regex_module
        from lexicon.pinyin_utils import expand_pinyin_wildcards

        if '@' in regex_pattern:
            expanded_patterns = expand_pinyin_wildcards(regex_pattern)
            if len(expanded_patterns) > 1:
                alternative_patterns = []
                for pattern in expanded_patterns:
                    expanded = self._expand_regex_with_pinyin_internal(pattern, enable_homophone)
                    alternative_patterns.append(f"(?:{expanded})")
                return '|'.join(alternative_patterns)
            else:
                regex_pattern = expanded_patterns[0]

        return self._expand_regex_with_pinyin_internal(regex_pattern, enable_homophone)

    def _expand_regex_with_pinyin_internal(self, regex_pattern: str, enable_homophone: bool = False) -> str:
        import re as regex_module

        result_parts = []
        i = 0
        in_bracket = False
        bracket_content = []
        accumulated_pinyin = ""

        def flush_pinyin():
            nonlocal accumulated_pinyin
            if accumulated_pinyin:
                syllables = self._split_pinyin_syllables(accumulated_pinyin)

                if enable_homophone:
                    from lexicon.pinyin_utils import get_similar_pinyin

                    for syllable in syllables:
                        syllable_chars = set()

                        base_chars = self._expand_with_pinyin(syllable)
                        syllable_chars.update(base_chars)

                        similar_pinyins = get_similar_pinyin(syllable)
                        for similar in similar_pinyins:
                            similar_chars = self._expand_with_pinyin(similar)
                            syllable_chars.update(similar_chars)

                        syllable_chars.discard(syllable)

                        if len(syllable_chars) > 1:
                            escaped_chars = [regex_module.escape(c) for c in syllable_chars]
                            result_parts.append(f"[{''.join(escaped_chars)}]")
                        elif len(syllable_chars) == 1:
                            result_parts.append(regex_module.escape(list(syllable_chars)[0]))
                        else:
                            result_parts.append(regex_module.escape(syllable))
                else:
                    for syllable in syllables:
                        expanded = self._expand_with_pinyin(syllable)
                        if len(expanded) > 1:
                            escaped_chars = [regex_module.escape(c) for c in expanded]
                            result_parts.append(f"[{''.join(escaped_chars)}]")
                        else:
                            result_parts.append(syllable)

                accumulated_pinyin = ""

        while i < len(regex_pattern):
            char = regex_pattern[i]

            if char == '[' and (i == 0 or regex_pattern[i-1] != '\\'):
                flush_pinyin()
                in_bracket = True
                bracket_content = [char]
                i += 1
            elif char == ']' and in_bracket and (i == 0 or regex_pattern[i-1] != '\\'):
                in_bracket = False
                bracket_content.append(char)
                result_parts.append(''.join(bracket_content))
                bracket_content = []
                i += 1
            elif in_bracket:
                bracket_content.append(char)
                i += 1
            elif char == '\\' and i + 1 < len(regex_pattern):
                flush_pinyin()
                result_parts.append(char + regex_pattern[i + 1])
                i += 2
            elif char in '.^$*+?{}()|':
                flush_pinyin()
                result_parts.append(char)
                i += 1
            elif ord(char) > 127:
                flush_pinyin()
                result_parts.append(char)
                i += 1
            else:
                accumulated_pinyin += char
                i += 1

        flush_pinyin()

        return ''.join(result_parts)

    def _expand_with_homophone(self, pinyin_initials: str) -> set[str]:
        result = {pinyin_initials}

        SIMILAR_INITIALS_MAP = {
            "zh": ["z"],
            "z": ["zh"],
            "ch": ["c"],
            "sh": ["s"],
            "c": ["ch"],
            "s": ["sh"],
            "n": ["l"],
            "l": ["n"],
            "f": ["h"],
            "h": ["f"],
        }

        initials_list = list(pinyin_initials)
        variants_per_position = []

        for initial in initials_list:
            variants = {initial}
            if initial in SIMILAR_INITIALS_MAP:
                for sim in SIMILAR_INITIALS_MAP[initial]:
                    variants.add(sim[0] if len(sim) > 1 else sim)
            variants_per_position.append(sorted(variants))

        from itertools import product
        for combo in product(*variants_per_position):
            combo_str = "".join(combo)
            if len(combo_str) <= 20:
                result.add(combo_str)

        return result

    def _expand_with_homophone_full(self, full_pinyin: str) -> set[str]:
        result = {full_pinyin}

        from lexicon.pinyin_utils import get_similar_pinyin

        syllables = full_pinyin.split()

        from itertools import product
        variants_per_syllable = []
        for syllable in syllables:
            similar_pys = get_similar_pinyin(syllable)
            variants_per_syllable.append([syllable] + similar_pys)

        for combo in product(*variants_per_syllable):
            result.add(" ".join(combo))

        return result
