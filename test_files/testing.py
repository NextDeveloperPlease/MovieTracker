import requests
from bs4 import BeautifulSoup

# Ignore this file. It was for generating a sample HTML page for testing purposes.

url = "https://www.cinemark.com/theatres/id-meridian/cinemark-majestic-cinemas?gad_source=1&gad_campaignid=21320863670&gclid=Cj0KCQjwpf7CBhCfARIsANIETVr9mT_YmFb_aVZQJhipsY3c2kmYckiYoG5dQLgUfU9ODgKkcIIqVD8aApW8EALw_wcB&showDate=2025-07-05"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)

with open("page.html", "w", encoding="utf-8") as f:
    f.write(response.text)