import requests


class DictionaryAPI:
    @staticmethod
    def get_definition(word, api, preferred_pos=None):
        if api == "freedictionary":
            return FreeDictionaryAPI.get_definition(word, preferred_pos=preferred_pos)
        return None


class FreeDictionaryAPI:
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

    @staticmethod
    def get_definition(word, preferred_pos=None):
        try:
            r = requests.get(f"{FreeDictionaryAPI.BASE_URL}{word.lower()}", timeout=5)
            if r.status_code != 200:
                return None

            entries = r.json()
            parts = []

            first_entry = entries[0]
            phonetic = first_entry.get("phonetic", "")
            if not phonetic:
                for phonetic_entry in first_entry.get("phonetics", ""):
                    if phonetic_entry.get("text", ""):
                        phonetic = phonetic_entry.get("text", "")
                        break
            if phonetic:
                parts.append(phonetic + "\n")

            all_meanings = []
            for entry in entries:
                all_meanings.extend(entry.get("meanings", []))

            filtered_meanings = [
                                    m for m in all_meanings
                                    if preferred_pos and m.get(
                    "partOfSpeech") in preferred_pos
                                ] or all_meanings

            if not filtered_meanings:
                return None

            for meaning in filtered_meanings:
                pos = meaning.get("partOfSpeech")
                if pos:
                    parts.append(f"{pos}:\n")

                for i, d in enumerate(meaning.get("definitions", [])[:3], start=1):
                    definition = d.get("definition", "")
                    example = d.get("example")
                    parts.append(f"{i}. {definition}")
                    if example:
                        parts.append(f"   Example: {example}")

                synonyms = meaning.get("synonyms", [])
                if synonyms:
                    parts.append(f"Synonyms: {', '.join(synonyms[:8])}")
                antonyms = meaning.get("antonyms", [])
                if antonyms:
                    parts.append(f"Antonyms: {', '.join(antonyms[:8])}")

            if first_entry.get("sourceUrls"):
                parts.append(f"\nSource: {first_entry['sourceUrls'][0]}")

            return "\n".join(parts)

        except requests.RequestException:
            return None
