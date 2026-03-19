import requests


class DictionaryAPI:
    """Factory to support multiple dictionary APIs later on."""

    @staticmethod
    def get_definition(word, api="freedictionary"):
        if api == "freedictionary":
            return FreeDictionaryAPI.get_definition(word)
        # Add more APIs here (e.g. Wordnik, SpanishDict, etc.)
        return None


class FreeDictionaryAPI:
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

    @staticmethod
    def get_definition(word):
        url = f"{FreeDictionaryAPI.BASE_URL}/{word.lower()}"
        try:
            r = requests.get(url, timeout=5)

            if r.status_code == 200:
                data = r.json()
                # Each entry can have multiple meanings and definitions
                meanings = data[0].get("meanings", [])
                definitions = []

                for meaning in meanings:
                    for d in meaning.get("definitions", []):
                        definition = d.get("definition")
                        if definition:
                            definitions.append(definition)

                # Return a joined string for convenience
                return "; ".join(definitions[:3]) if definitions else None

            elif r.status_code == 404:
                return None  # word not found
            else:
                r.raise_for_status()

        except requests.RequestException:
            return None
