from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable
import requests


@dataclass
class DictionarySense:
    definition: str
    examples: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)


@dataclass
class DictionaryEntry:
    language_code: str
    language_name: str
    part_of_speech: str | None
    pronunciations: list[str] = field(default_factory=list)
    senses: list[DictionarySense] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)


@dataclass
class DictionaryResult:
    word: str
    entries: list[DictionaryEntry]
    source_url: str | None = None


class DictionaryProvider(ABC):
    @abstractmethod
    def get_definition(
            self,
            word: str,
            *,
            language: str = "en",
            preferred_pos: Iterable[str] | None = None,
    ) -> str | None:
        raise NotImplementedError


class DictionaryFormatter:
    @staticmethod
    def format_result(
            result: DictionaryResult,
            preferred_pos: Iterable[str] | None = None,
            max_senses: int = 3,
            max_related: int = 8,
    ) -> str | None:
        preferred = set(preferred_pos or [])

        entries = [
                      entry for entry in result.entries
                      if not preferred or entry.part_of_speech in preferred
                  ] or result.entries

        if not entries:
            return None

        parts: list[str] = []

        pronunciation = next(
            (
                p
                for entry in entries
                for p in entry.pronunciations
                if p
            ),
            "",
        )
        if pronunciation:
            parts.append(pronunciation)
            parts.append("")

        grouped_by_language: dict[str, list[DictionaryEntry]] = {}
        for entry in entries:
            label = f"{entry.language_name} ({entry.language_code})"
            grouped_by_language.setdefault(label, []).append(entry)

        for language_label, language_entries in grouped_by_language.items():
            parts.append(f"[{language_label}]")

            for entry in language_entries:
                if entry.part_of_speech:
                    parts.append(f"{entry.part_of_speech}:")

                for i, sense in enumerate(entry.senses[:max_senses], start=1):
                    if sense.definition:
                        parts.append(f"{i}. {sense.definition}")
                    if sense.examples:
                        parts.append(f"   Example: {sense.examples[0]}")

                synonyms = entry.synonyms[:] or [
                    s for sense in entry.senses for s in sense.synonyms
                ]
                antonyms = entry.antonyms[:] or [
                    a for sense in entry.senses for a in sense.antonyms
                ]

                unique_synonyms = list(dict.fromkeys(synonyms))
                unique_antonyms = list(dict.fromkeys(antonyms))

                if unique_synonyms:
                    parts.append(
                        f"Synonyms: {', '.join(unique_synonyms[:max_related])}")
                if unique_antonyms:
                    parts.append(
                        f"Antonyms: {', '.join(unique_antonyms[:max_related])}")

                parts.append("")

        if result.source_url:
            parts.append(f"Source: {result.source_url}")

        return "\n".join(part for part in parts if part is not None).strip()


class FreeDictionaryAPI(DictionaryProvider):
    BASE_URL = "https://freedictionaryapi.com/api/v1/entries"
    TIMEOUT = 5

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

    def get_definition(
            self,
            word: str,
            *,
            language: str = "en",
            preferred_pos: Iterable[str] | None = None,
    ) -> str | None:
        result = self.lookup(word, language=language)
        if not result:
            return None
        return DictionaryFormatter.format_result(result, preferred_pos=preferred_pos)

    def lookup(self, word: str, *, language: str = "en") -> DictionaryResult | None:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{language.lower()}/{word.strip()}",
                timeout=self.TIMEOUT,
            )
            if response.status_code != 200:
                return None

            data = response.json()
            entries_data = data.get("entries", [])
            if not entries_data:
                return None

            entries: list[DictionaryEntry] = []
            for raw_entry in entries_data:
                senses = [
                    DictionarySense(
                        definition=sense.get("definition", ""),
                        examples=sense.get("examples", []) or [],
                        synonyms=sense.get("synonyms", []) or [],
                        antonyms=sense.get("antonyms", []) or [],
                    )
                    for sense in raw_entry.get("senses", [])
                ]

                pronunciations = [
                    p.get("text", "")
                    for p in raw_entry.get("pronunciations", [])
                    if p.get("text")
                ]

                lang = raw_entry.get("language", {}) or {}

                entries.append(
                    DictionaryEntry(
                        language_code=lang.get("code", language),
                        language_name=lang.get("name", language),
                        part_of_speech=raw_entry.get("partOfSpeech"),
                        pronunciations=pronunciations,
                        senses=senses,
                        synonyms=raw_entry.get("synonyms", []) or [],
                        antonyms=raw_entry.get("antonyms", []) or [],
                    )
                )

            return DictionaryResult(
                word=data.get("word", word),
                entries=entries,
                source_url=(data.get("source") or {}).get("url"),
            )

        except requests.RequestException:
            return None
        except (ValueError, TypeError):
            return None


class DictionaryAPI:
    _providers: dict[str, DictionaryProvider] = {
        "freedictionary": FreeDictionaryAPI(),
    }

    @classmethod
    def has_provider(cls, name: str) -> bool:
        return name.lower() in cls._providers

    @classmethod
    def register_provider(cls, name: str, provider: DictionaryProvider) -> None:
        cls._providers[name.lower()] = provider

    @classmethod
    def get_definition(
            cls,
            word: str,
            api: str = "freedictionary",
            *,
            language: str = "en",
            preferred_pos: Iterable[str] | None = None,
    ) -> str | None:
        provider = cls._providers.get(api.lower())
        if not provider:
            return None

        return provider.get_definition(
            word,
            language=language,
            preferred_pos=preferred_pos,
        )


class DefinitionError(Exception):
    pass


class UnsupportedAPIError(DefinitionError):
    pass


class InvalidRequestError(DefinitionError):
    pass


@dataclass(frozen=True)
class DefinitionQuery:
    word: str
    api: str = "freedictionary"
    language: str = "en"
    preferred_pos: tuple[str, ...] | None = None


class DefinitionService:
    DEFAULT_API = "freedictionary"

    LANGUAGE_HINTS = {
        "en": {
            "to ": ("verb",),
            "the ": ("noun",),
            "a ": ("noun",),
            "an ": ("noun",),
        },
        "es": {
            "el ": ("noun",),
            "la ": ("noun",),
            "los ": ("noun",),
            "las ": ("noun",),
        },
        "fr": {
            "le ": ("noun",),
            "la ": ("noun",),
            "les ": ("noun",),
            "un ": ("noun",),
            "une ": ("noun",),
        },
        "de": {
            "der ": ("noun",),
            "die ": ("noun",),
            "das ": ("noun",),
            "ein ": ("noun",),
            "eine ": ("noun",),
        },
    }

    FALLBACK_POS = {
        "en": None,
        "es": None,
        "fr": None,
        "de": None,
    }

    @classmethod
    def fetch_definition(
            cls,
            *,
            word_raw: str,
            api: str | None = None,
            language: str | None = None,
    ) -> str | None:
        query = cls.build_query(word_raw=word_raw, api=api, language=language)

        if not DictionaryAPI.has_provider(query.api):
            raise UnsupportedAPIError(f"Unsupported API: {query.api}")

        return DictionaryAPI.get_definition(
            word=query.word,
            api=query.api,
            language=query.language,
            preferred_pos=query.preferred_pos,
        )

    @classmethod
    def build_query(
            cls,
            *,
            word_raw: str,
            api: str | None = None,
            language: str | None = None,
    ) -> DefinitionQuery:
        word = (word_raw or "").strip()
        if not word:
            raise InvalidRequestError("No word provided")

        api_name = (api or cls.DEFAULT_API).strip().lower()
        language_code = (language or "en").strip().lower()

        normalized_word, preferred_pos = cls.extract_preferred_pos(
            word=word,
            language=language_code,
        )

        return DefinitionQuery(
            word=normalized_word,
            api=api_name,
            language=language_code,
            preferred_pos=preferred_pos,
        )

    @classmethod
    def extract_preferred_pos(
            cls,
            *,
            word: str,
            language: str,
    ) -> tuple[str, tuple[str, ...] | None]:
        lowered = word.lower()

        for prefix, pos in cls.LANGUAGE_HINTS.get(language, {}).items():
            if lowered.startswith(prefix):
                return word[len(prefix):].strip(), pos

        fallback = cls.FALLBACK_POS.get(language)
        return word, fallback
