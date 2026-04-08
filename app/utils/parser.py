"""
App Utils — Query Parser
Extracts structured information from raw user error input.
"""
import re
from typing import Optional


LANGUAGE_PATTERNS = {
    "java": [
        r"NullPointerException", r"ArrayIndexOutOfBoundsException",
        r"ClassCastException", r"StackOverflowError", r"OutOfMemoryError",
        r"ConcurrentModificationException", r"IllegalArgumentException",
        r"\.java:", r"at com\.", r"at org\.",
    ],
    "python": [
        r"KeyError", r"AttributeError", r"IndexError", r"TypeError",
        r"ValueError", r"RecursionError", r"ModuleNotFoundError",
        r"ImportError", r"ZeroDivisionError", r"NameError",
        r"Traceback \(most recent call last\)",
        r"File \".*\.py\"",
    ],
    "javascript": [
        r"TypeError: Cannot read propert",
        r"ReferenceError", r"SyntaxError", r"Unhandled Promise",
        r"\.js:", r"at Object\.", r"Promise rejection",
    ],
    "react": [
        r"Maximum update depth exceeded",
        r"Cannot update a component",
        r"Each child in a list",
        r"Hook",
    ],
    "sql": [
        r"Deadlock", r"deadlock", r"syntax error at or near",
        r"ORA-", r"N\+1", r"relation .* does not exist",
    ],
    "c++": [
        r"Segmentation fault", r"segfault", r"SIGSEGV",
        r"double free", r"heap-buffer-overflow",
    ],
    "docker": [
        r"OOMKilled", r"Exit Code 137", r"container.*crash",
        r"ImagePullBackOff", r"CrashLoopBackOff",
    ],
}


def detect_language(text: str) -> Optional[str]:
    """
    Detect programming language from error text using pattern matching.
    Returns the most likely language or None.
    """
    text_lower = text
    scores: dict[str, int] = {}

    for lang, patterns in LANGUAGE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[lang] = scores.get(lang, 0) + 1

    if not scores:
        return None

    return max(scores, key=scores.get)


def extract_error_type(text: str) -> str:
    """
    Extract the primary error type from text.
    Handles formats like:
    - "NullPointerException at UserService.java:42"
    - "Error: Cannot read property 'x' of undefined"
    - "Traceback...\nKeyError: 'name'"
    """
    patterns = [
        r"([A-Z][a-zA-Z]+(?:Error|Exception|Fault|Warning|Problem))",
        r"^([A-Z][a-zA-Z]+Error):",
        r"([A-Z][a-zA-Z]*Exception)",
        r"Error: (.+?)(?:\n|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1).strip()

    # Fallback: first line
    return text.split("\n")[0][:100].strip()


def parse_raw_input(
    raw_input: str,
    language: Optional[str] = None,
    context: Optional[str] = None,
) -> dict:
    """
    Parse raw user error input into a structured query dict.
    Used as a fast fallback if the LLM query rewriter fails.
    """
    detected_lang = language or detect_language(raw_input) or "unknown"
    error_type = extract_error_type(raw_input)

    return {
        "error_type": error_type,
        "language": detected_lang,
        "context": context or "No additional context provided",
        "rewritten_query": f"{error_type} error in {detected_lang}: {raw_input[:200]}",
    }
