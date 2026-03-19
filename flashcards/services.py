import requests


class DictionaryAPI:
    @staticmethod
    def get_definition(word, api="freedictionary", preferred_pos=None):
        if api == "freedictionary":
            return FreeDictionaryAPI.get_definition(word, preferred_pos=preferred_pos)
        return None


class FreeDictionaryAPI:
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

    @staticmethod
    def get_definition(word, preferred_pos=None):
        """
        Fetch and format a definition from the Free Dictionary API.
        Shows only the preferred parts of speech (list), or the first available if
        none found.
        """
        url = f"{FreeDictionaryAPI.BASE_URL}/{word.lower()}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return None

            entries = r.json()
            parts = []

            # Word basics
            first_entry = entries[0]
            word_text = first_entry.get("word", word)
            phonetic = first_entry.get("phonetic", "")
            parts.append(
                f"{word_text} {phonetic}" if phonetic else f"{word_text}")

            # Gather all meanings
            all_meanings = []
            for entry in entries:
                all_meanings.extend(entry.get("meanings", []))

            # Filter by preferred parts of speech (can be list)
            filtered_meanings = []
            if preferred_pos:
                for m in all_meanings:
                    if m.get("partOfSpeech") in preferred_pos:
                        filtered_meanings.append(m)

            # Fallback to all meanings if nothing matches
            if not filtered_meanings:
                filtered_meanings = all_meanings

            if not filtered_meanings:
                return None

            # Show up to 2 parts of speech
            for meaning in filtered_meanings[:2]:
                pos = meaning.get("partOfSpeech")
                if pos:
                    parts.append(f"\n{pos}:\n")

                for i, d in enumerate(meaning.get("definitions", [])[:3], start=1):
                    definition = d.get("definition", "")
                    example = d.get("example")
                    parts.append(f"{i}. {definition}")
                    if example:
                        parts.append(f"   Example: {example}")

                synonyms = meaning.get("synonyms", [])
                if synonyms:
                    parts.append(f"Synonyms: {', '.join(synonyms[:8])}")

            # Source URL
            for entry in entries:
                if entry.get("sourceUrls"):
                    parts.append(f"\nSource: {entry['sourceUrls'][0]}")
                    break

            return "\n".join(parts)

        except requests.RequestException:
            return None
