import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import NOT_FOUND

current_page = 1
proceed = True
data = []

while proceed:

    print(f"scraping page {current_page}")
    url = f"https://books.toscrape.com/catalogue/page-{current_page}.html"
    # proxies={'http': 'http://customer-[your_username]:[your_password]_@pr.oxylabs.io:7777'}
    proxies = proxies
    page = requests.get(url=url, proxies=proxies)

    soup = BeautifulSoup(
        page.text, "html.parser"
    )  # iw ill see trhe available parser in the beautiful soup documentation

    if soup.title.text == NOT_FOUND:
        proceed = False
    else:
        books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
        for book in books:
            item = {}

            item["Title"] = book.find("img").attrs["alt"]

            item["Link"] = (
                "https://books.toscrape.com/catalogue/" + book.find("a").attrs["href"]
            )

            item["Price"] = book.find("p", class_="price_color").text[2:]
            item["Stock"] = book.find("p", class_="instock availability").text.strip()

            data.append(item)
    current_page += 1

df = pd.DataFrame(data=data)
df.to_excel("books.xlsx")
df.to_csv("books.csv")
