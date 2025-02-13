from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def scrape():
    url = "https://www.theverge.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to retrieve the website.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    for article in soup.select('a[class="_1lkmsmo1"]'):
        title = article.get_text(strip=True)
        link = article.get("href")

        if link and not link.startswith("http"):
            link = f"https://www.theverge.com{link}"

        article_response = requests.get(link, headers=headers)
        article_soup = BeautifulSoup(article_response.text, "html.parser")

        date_tag = article_soup.find("time")
        if not date_tag or not date_tag.has_attr("datetime"):
            continue  
        try:
            date_str = date_tag["datetime"]
            article_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)

            if article_date >= datetime(2022, 1, 1):
                headlines.append((title, link, article_date))
        except ValueError:
            continue  

    headlines.sort(key=lambda x: x[2], reverse=True)

    return headlines

@app.route('/')
def home():
    headlines = scrape()
    return render_template('index.html', headlines=headlines)

if __name__ == "__main__":
    app.run(debug=True)
