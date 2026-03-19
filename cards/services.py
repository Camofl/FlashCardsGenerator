import requests


class DictionaryAPI:
    @staticmethod
    def get_definition(word, api, preferred_pos=None):
        if api == "freedictionary":
            return FreeDictionaryAPI.get_definition(word, preferred_pos=preferred_pos)
        return None


class FreeDictionaryAPI:
    BASE_URL = "https://freedictionaryapi.com/api/v1/entries/en/"

    @staticmethod
    def get_definition(word, preferred_pos=None):
        try:
            r = requests.get(f"{FreeDictionaryAPI.BASE_URL}{word.lower()}", timeout=5)
            if r.status_code != 200:
                return None

            data = r.json()
            entries = data.get("entries", [])
            if not entries:
                return None

            parts = []

            pronunciation = ""
            for p in entries[0].get("pronunciations", []):
                if p.get("text"):
                    pronunciation = p["text"]
                    break

            if pronunciation:
                parts.append(pronunciation + "\n")

            filtered_entries = [
                e
                for e in entries
                if preferred_pos and e.get("partOfSpeech") in preferred_pos
            ] or entries

            if not filtered_entries:
                return None

            for entry in filtered_entries:
                pos = entry.get("partOfSpeech")
                if pos:
                    parts.append(f"{pos}:\n")

                senses = entry.get("senses", [])
                for i, sense in enumerate(senses[:3], start=1):
                    definition = sense.get("definition", "")
                    if definition:
                        parts.append(f"{i}. {definition}")

                    examples = sense.get("examples", [])
                    if examples:
                        parts.append(f"   Example: {examples[0]}")

                synonyms = entry.get("synonyms", [])
                if not synonyms:
                    for sense in senses:
                        synonyms.extend(sense.get("synonyms", []))
                if synonyms:
                    parts.append(f"Synonyms: {', '.join(synonyms[:8])}")

                antonyms = entry.get("antonyms", [])
                if not antonyms:
                    for sense in senses:
                        antonyms.extend(sense.get("antonyms", []))
                if antonyms:
                    parts.append(f"Antonyms: {', '.join(antonyms[:8])}")

            source_url = data.get("source", {}).get("url")
            if source_url:
                parts.append(f"\nSource: {source_url}")

            return "\n".join(parts)

        except requests.RequestException:
            return None
        except (ValueError, TypeError):
            return None