import requests


def access_to_dictionary(word):
    url = "https://en.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "titles": word,
        "prop": "extracts",
        "format": "json",
        "explaintext": True,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print(response.json())
        return print(f"{word} exists in the dictionary")
    else:
        return print(f"{word} does not exist in the dictionary")

access_to_dictionary("kurwa")