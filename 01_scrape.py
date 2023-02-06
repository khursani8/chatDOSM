import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import time
from pathlib import Path

url = "https://open.dosm.gov.my/data-catalogue"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

headlines = soup.find("div",{"class":"relative w-full"}).find_all("li")
url_map = {}
for i in headlines:
    a = i.find("a")
    if a is None:
        continue
    href = a.attrs["href"]
    if "dosm-public-economy" in href:
        types = "dosm-public-economy"
        link = "_".join(href.replace("/data-catalogue/dosm-public-economy_","").split("_")[:-1])
        url = "https://storage.googleapis.com/dosm-public-economy/"+link+".parquet"
    elif "dosm-public-mets" in href:
        types = "dosm-public-mets"
        link = "_".join(href.replace("/data-catalogue/dosm-public-mets_","").split("_")[:-1])
        url = "https://storage.googleapis.com/dosm-public-mets/"+link+".parquet"
    elif "dosm-public-pricecatcher" in href: # https://storage.googleapis.com/dosm-public-pricecatcher/lookup_item.parquet
        types = "dosm-public-pricecatcher"
        link = "_".join(href.replace("/data-catalogue/dosm-public-pricecatcher_","").split("_")[:-1])
        url = "https://storage.googleapis.com/dosm-public-pricecatcher/"+link+".parquet"
    elif "dosm-public-healthcare" in href: # https://storage.googleapis.com/dosm-public-healthcare/lookup_item.parquet
        types = "dosm-public-healthcare"
        link = "_".join(href.replace("/data-catalogue/dosm-public-healthcare_","").split("_")[:-1])
        url = "https://storage.googleapis.com/dosm-public-healthcare/"+link+".parquet"
    else:
        print("skip because too lazy")
        print(href)
    try:
        fn = "data/"+f"{types}_x_"+url.split("/")[-1]
        if Path(fn).is_file():
            continue
        df = pd.read_parquet(url)
        df.to_csv(fn)
        url_map[a.text] = url
        time.sleep(0.1)
    except:
        print("error",link,url)
        break

import json
with open('urls.json', 'w') as fp:
    json.dump(url_map, fp)