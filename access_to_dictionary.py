import requests

def check(city):
    URL = f"https://www.geonames.org/search.html?q={city}"
    response = requests.request("GET", URL)
    print(response.text)
    if 'we have found no places' in response.text.lower():  # Case-insensitive match
        return False
    else:
        return True





