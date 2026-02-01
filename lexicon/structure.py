"""Structure detection for Chinese words."""

import re

# Structure patterns for Chinese words
STRUCTURE_PATTERNS = {
    "AABB": r"^(.)\1(.)\2$",
    "ABAB": r"^(.)(.)\1\2$",
    "ABAC": r"^(.)(.)\1(.)$",
    "ABCC": r"^(.)(.)(.)\3$",
    "AABC": r"^(.)\1(.)(.)$",
    "ABCB": r"^(.)(.)(.)\2$",
}


def detect_structure(word: str) -> str | None:
    """Detect the structure pattern of a Chinese word.
    
    Args:
        word: A Chinese word string
        
    Returns:
        Structure type (AABB, ABAB, ABAC, ABCC, AABC, ABCB) or None if no match
        
    Examples:
        >>> detect_structure("高高兴兴")
        "AABB"
        >>> detect_structure("研究研究")
        "ABAB"
        >>> detect_structure("一心一意")
        "ABAC"
    """
    if not word or len(word) < 2:
        return None
    
    # Try each pattern in order (ordered by specificity)
    # Check AABB pattern: (.)\1(.)\2
    if len(word) == 4 and re.match(STRUCTURE_PATTERNS["AABB"], word):
        return "AABB"
    
    # Check ABAB pattern: (.)(.)\\1\\2
    if len(word) == 4 and re.match(STRUCTURE_PATTERNS["ABAB"], word):
        return "ABAB"
    
    # Check ABAC pattern: (.)(.)\\1(.)
    if len(word) == 4 and re.match(STRUCTURE_PATTERNS["ABAC"], word):
        return "ABAC"
    
    # Check ABCC pattern: (.)(.)(.)\\3
    if len(word) == 4 and re.match(STRUCTURE_PATTERNS["ABCC"], word):
        return "ABCC"
    
    # Check AABC pattern: (.)\1(.)(.)
    if len(word) == 4 and re.match(STRUCTURE_PATTERNS["AABC"], word):
        return "AABC"
    
    # Check ABCB pattern: (.)(.)(.)\2
    if len(word) == 4 and re.match(STRUCTURE_PATTERNS["ABCB"], word):
        return "ABCB"
    
    return None
