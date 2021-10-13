"""
Downloads the articles from wikipedia
Can take hours to run!

"""


import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlretrieve

base_url = 'https://dumps.wikimedia.org/enwiki/'
index = requests.get(base_url).text
soup_index = BeautifulSoup(index, 'html.parser')
# Find the links on the page
dumps = [a['href'] for a in soup_index.find_all('a') if
         a.has_attr('href')]
print(dumps)

dump_url = base_url + '20210901/'     ########################### Change this to get newest version ##########
# Retrieve the html
dump_html = requests.get(dump_url).text
# Convert to a soup
soup_dump = BeautifulSoup(dump_html, 'html.parser')
# Find list elements with the class file
list_ = soup_dump.find_all('li', {'class': 'file'})

folder = Path(r"C:\Users\FPLC\Desktop\wikipidia")
url = 'https://dumps.wikimedia.org/enwiki/20210901/'

for i in range(2, 124, 2):
    file_url = list_[i].find("a").text
    full_url = url + file_url
    print(full_url)
    urlretrieve(full_url, (folder / file_url).resolve())
