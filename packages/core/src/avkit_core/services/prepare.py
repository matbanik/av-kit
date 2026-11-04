"""TextPreparationService — stateless TTS cleanup pipeline."""

from __future__ import annotations

import re

from avkit_core.domain.errors import SpacyModelNotFoundError, ValidationError
from avkit_core.domain.tts import SPACY_MODEL

PREPARE_STEP_IDS: tuple[str, ...] = (
    "punctuation",
    "symbols",
    "numbers",
    "currency",
    "all_caps",
    "chapter_markers",
    "urls_emails",
    "page_numbers",
    "whitespace",
    "chunk",
    "kokoro",
)
PREPARE_ORDER = PREPARE_STEP_IDS
PREPARE_DEFAULT_ON = frozenset(step for step in PREPARE_STEP_IDS if step != "chapter_markers")
_ONES = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")


def _int_to_words(value: int) -> str:
    if value < 20:
        return _ONES[value]
    if value < 100:
        tens, ones = divmod(value, 10)
        if ones == 0:
            return _TENS[tens]
        return f"{_TENS[tens]}-{_ONES[ones]}"
    if value < 1000:
        hundreds, rest = divmod(value, 100)
        if rest == 0:
            return f"{_ONES[hundreds]} hundred"
        return f"{_ONES[hundreds]} hundred {_int_to_words(rest)}"
    return str(value)


def _spell_numbers(text: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        number = int(match.group(0))
        if number > 999:
            return match.group(0)
        return _int_to_words(number)

    return re.sub(r"\b\d+\b", _replace, text)


def _punctuation(text: str) -> str:
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"\?{2,}", "?", text)
    return text


def _symbols(text: str) -> str:
    text = text.replace("&", " and ")
    text = text.replace("%", " percent ")
    return text


def _currency(text: str) -> str:
    return re.sub(r"\$(\d+(?:\.\d+)?)", r"\1 dollars", text)


def _all_caps(text: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        word = match.group(0)
        if len(word) <= 2:
            return word
        return word.title()

    return re.sub(r"\b[A-Z]{2,}\b", _replace, text)


def _chapter_markers(text: str) -> str:
    return re.sub(r"\bCHAPTER\s+(\d+)\b", r"Chapter \1", text, flags=re.IGNORECASE)


def _urls_emails(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\b\S+@\S+\.\S+\b", "", text)
    return text


def _page_numbers(text: str) -> str:
    return re.sub(r"(?m)^\s*\d{1,3}\s*$", "", text)


def _whitespace(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).replace(" \n", "\n").strip()


def _comma_split(sentence: str, max_chars: int) -> list[str]:
    parts = [part.strip() for part in sentence.split(",") if part.strip()]
    if len(parts) < 2:
        words = sentence.split()
        packed: list[str] = []
        current: list[str] = []
        for word in words:
            trial = " ".join([*current, word])
            if current and len(trial) > max_chars:
                packed.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            packed.append(" ".join(current))
        return packed or [sentence]
    groups: list[str] = []
    current_text = ""
    for part in parts:
        trial = part if not current_text else f"{current_text}, {part}"
        if current_text and len(trial) > max_chars:
            groups.append(current_text)
            current_text = part
        else:
            current_text = trial
    if current_text:
        groups.append(current_text)
    return groups


def _chunk(text: str, chunk_max_chars: int) -> str:
    try:
        import spacy
    except ImportError as exc:
        raise SpacyModelNotFoundError(f"{SPACY_MODEL} is not available") from exc
    try:
        nlp = spacy.load(SPACY_MODEL)
    except OSError as exc:
        raise SpacyModelNotFoundError(f"{SPACY_MODEL} is not available") from exc
    except Exception as exc:
        raise SpacyModelNotFoundError(f"{SPACY_MODEL} is not available") from exc
    sentences = [sent.text.strip() for sent in nlp(text).sents if sent.text.strip()]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > chunk_max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_comma_split(sentence, chunk_max_chars))
            continue
        trial = sentence if not current else f"{current} {sentence}"
        if current and len(trial) > chunk_max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = trial
    if current:
        chunks.append(current)
    return "\n\n".join(chunks)


def _space_acronyms(text: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        return " ".join(match.group(0))

    return re.sub(r"\b[A-Z]{2,}\b", _replace, text)


def _limit_sentence_words(text: str, limit: int = 25) -> str:
    pieces: list[str] = []
    for raw in re.split(r"(?<=[.!?])\s+", text):
        words = raw.split()
        if len(words) <= limit:
            pieces.append(raw.strip())
            continue
        for index in range(0, len(words), limit):
            chunk = " ".join(words[index : index + limit])
            if not chunk.endswith((".", "!", "?")):
                chunk = f"{chunk}."
            pieces.append(chunk)
    return " ".join(part for part in pieces if part)


def _kokoro(text: str) -> str:
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = text.replace("…", ".")
    text = re.sub(r"\.{3,}", ".", text)
    text = _spell_numbers(text)
    text = _space_acronyms(text)
    text = _limit_sentence_words(text)
    return _whitespace(text)


_STEPS = {
    "punctuation": _punctuation,
    "symbols": _symbols,
    "numbers": _spell_numbers,
    "currency": _currency,
    "all_caps": _all_caps,
    "chapter_markers": _chapter_markers,
    "urls_emails": _urls_emails,
    "page_numbers": _page_numbers,
    "whitespace": _whitespace,
    "kokoro": _kokoro,
}


class TextPreparationService:
    """Stateless prepare pipeline. Order is PREPARE_ORDER, not enabled_steps order."""

    def prepare(
        self,
        text: str,
        enabled_steps: list[str],
        chunk_max_chars: int | None = None,
    ) -> str:
        if not isinstance(text, str):
            raise ValidationError("text must be a str")
        unknown = [step for step in enabled_steps if step not in PREPARE_STEP_IDS]
        if unknown:
            raise ValidationError("unknown prepare step id")
        enabled = set(enabled_steps)
        result = text
        width = 250 if chunk_max_chars is None else chunk_max_chars
        if width < 1:
            raise ValidationError("chunk_max_chars must be positive")
        for step in PREPARE_ORDER:
            if step not in enabled:
                continue
            if step == "chunk":
                result = _chunk(result, width)
            else:
                result = _STEPS[step](result)
        return result
